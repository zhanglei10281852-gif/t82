<template>
  <div class="bookings-page">
    <div class="page-header">
      <h2>预订管理</h2>
      <div class="header-actions">
        <a-button type="primary" @click="openCreateModal">
          <template #icon><PlusOutlined /></template>
          新增预订
        </a-button>
        <a-select v-model:value="statusFilter" placeholder="全部状态" style="width: 140px" allow-clear>
          <a-select-option value="pending">待确认</a-select-option>
          <a-select-option value="confirmed">已确认</a-select-option>
          <a-select-option value="checked_in">已入住</a-select-option>
          <a-select-option value="checked_out">已退房</a-select-option>
          <a-select-option value="cancelled">已取消</a-select-option>
        </a-select>
        <a-select v-if="auth.isAdmin" v-model:value="homestayFilter" placeholder="全部民宿" style="width: 160px" allow-clear>
          <a-select-option v-for="h in homestays" :key="h.id" :value="h.id">
            {{ h.name }}
          </a-select-option>
        </a-select>
        <a-button type="primary" @click="loadBookings">
          <template #icon><SearchOutlined /></template>
          查询
        </a-button>
      </div>
    </div>

    <a-table :columns="columns" :data-source="bookings" :loading="loading" row-key="id" :pagination="{ pageSize: 10 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="statusColor(record.status)">
            {{ statusText(record.status) }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'dates'">
          <div>{{ record.check_in_date }} 至 {{ record.check_out_date }}</div>
          <div style="font-size: 12px; color: #999">共{{ nights(record) }}晚</div>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="viewDetail(record)">详情</a-button>
          <a-divider type="vertical" />
          <template v-if="record.status === 'pending' && canManage(record)">
            <a-button type="link" @click="confirmBooking(record)">确认</a-button>
            <a-divider type="vertical" />
            <a-button type="link" danger @click="rejectBooking(record)">拒绝</a-button>
          </template>
          <template v-else-if="record.status === 'confirmed' && canManage(record)">
            <a-button type="link" @click="checkIn(record)">办理入住</a-button>
            <a-divider type="vertical" />
            <a-button type="link" danger @click="cancelBooking(record)">取消</a-button>
          </template>
          <template v-else-if="record.status === 'checked_in' && canManage(record)">
            <a-button type="link" @click="checkOut(record)">办理退房</a-button>
          </template>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="rejectModalOpen" title="拒绝预订" @ok="submitReject">
      <a-textarea v-model:value="rejectReason" placeholder="请输入拒绝原因" :rows="4" />
    </a-modal>

    <a-modal
      v-model:open="createModalOpen"
      title="新增预订"
      @ok="submitBooking"
      :confirm-loading="submitting"
      width="600px"
    >
      <a-form :model="bookingForm" layout="vertical" ref="formRef">
        <a-row :gutter="16">
          <a-col :span="24">
            <a-form-item label="选择民宿" required>
              <a-select
                v-model:value="bookingForm.homestay_id"
                placeholder="请选择民宿"
                @change="onHomestayChange"
                style="width: 100%"
              >
                <a-select-option v-for="h in allHomestays" :key="h.id" :value="h.id">
                  {{ h.name }} - {{ h.address }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="选择房间" required>
              <a-select
                v-model:value="bookingForm.room_id"
                placeholder="请先选择民宿"
                :disabled="!bookingForm.homestay_id"
                @change="onRoomChange"
                style="width: 100%"
              >
                <a-select-option v-for="r in availableRooms" :key="r.id" :value="r.id">
                  {{ r.name }} - {{ r.room_type }} - ¥{{ r.base_price }}/晚 - 最多{{ r.max_guests }}人
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="入住日期" required>
              <a-date-picker
                v-model:value="bookingForm.check_in_date"
                :disabled-date="disabledCheckInDate"
                @change="calculatePricePreview"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="离店日期" required>
              <a-date-picker
                v-model:value="bookingForm.check_out_date"
                :disabled-date="disabledCheckOutDate"
                @change="calculatePricePreview"
                style="width: 100%"
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="住客姓名" required>
              <a-input v-model:value="bookingForm.guest_name" placeholder="请输入住客姓名" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系电话" required>
              <a-input v-model:value="bookingForm.guest_phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="入住人数" required>
              <a-input-number
                v-model:value="bookingForm.guest_count"
                :min="1"
                :max="selectedRoom?.max_guests || 10"
                @change="calculatePricePreview"
                style="width: 100%"
              />
              <div v-if="selectedRoom" style="font-size: 12px; color: #999; margin-top: 4px">
                该房间最多容纳 {{ selectedRoom.max_guests }} 人
              </div>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="特殊需求">
              <a-textarea
                v-model:value="bookingForm.special_requests"
                placeholder="如有特殊需求请备注（如：高楼层、无烟房等）"
                :rows="3"
              />
            </a-form-item>
          </a-col>
        </a-row>

        <div v-if="pricePreview" class="price-preview">
          <a-divider />
          <h4 style="margin-bottom: 12px">价格明细</h4>
          <a-row :gutter="16">
            <a-col :span="8">
              <div class="price-item">
                <div class="price-label">基础总价</div>
                <div class="price-value">¥{{ pricePreview.base_total }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="price-item">
                <div class="price-label">优惠折扣</div>
                <div class="price-value">{{ pricePreview.discount === 1 ? '无' : (pricePreview.discount * 10).toFixed(1) + '折' }}</div>
              </div>
            </a-col>
            <a-col :span="8">
              <div class="price-item total">
                <div class="price-label">应付总价</div>
                <div class="price-value">¥{{ pricePreview.total_price }}</div>
              </div>
            </a-col>
          </a-row>
          <div v-if="pricePreview.breakdown && pricePreview.breakdown.length > 0" style="margin-top: 12px">
            <div style="font-size: 12px; color: #666; margin-bottom: 8px">每晚价格明细：</div>
            <a-tag
              v-for="(item, idx) in pricePreview.breakdown"
              :key="idx"
              :color="item.is_weekend ? 'orange' : (item.is_holiday ? 'red' : 'default')"
              style="margin-bottom: 4px"
            >
              {{ item.date }}: ¥{{ item.price }}
              <span v-if="item.is_holiday" style="font-size: 10px">(节假日)</span>
              <span v-else-if="item.is_weekend" style="font-size: 10px">(周末)</span>
            </a-tag>
          </div>
        </div>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined, PlusOutlined } from '@ant-design/icons-vue'
import { getBookings, updateBookingStatus, createBooking, calculatePrice } from '@/api/bookings'
import { getHomestays } from '@/api/homestays'
import { getRooms } from '@/api/rooms'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref(null)
const bookings = ref([])
const loading = ref(false)
const statusFilter = ref(undefined)
const homestayFilter = ref(undefined)
const homestays = ref([])
const allHomestays = ref([])
const availableRooms = ref([])
const rejectModalOpen = ref(false)
const rejectReason = ref('')
const currentBooking = ref(null)
const createModalOpen = ref(false)
const submitting = ref(false)
const pricePreview = ref(null)

const bookingForm = reactive({
  homestay_id: undefined,
  room_id: undefined,
  check_in_date: null,
  check_out_date: null,
  guest_name: '',
  guest_phone: '',
  guest_count: 1,
  special_requests: ''
})

const selectedRoom = computed(() => {
  if (!bookingForm.room_id) return null
  return availableRooms.value.find(r => r.id === bookingForm.room_id)
})

function disabledCheckInDate(current) {
  return current && current < dayjs().startOf('day')
}

function disabledCheckOutDate(current) {
  if (!bookingForm.check_in_date) return true
  return current && current <= dayjs(bookingForm.check_in_date)
}

function openCreateModal() {
  bookingForm.homestay_id = undefined
  bookingForm.room_id = undefined
  bookingForm.check_in_date = null
  bookingForm.check_out_date = null
  bookingForm.guest_name = ''
  bookingForm.guest_phone = ''
  bookingForm.guest_count = 1
  bookingForm.special_requests = ''
  availableRooms.value = []
  pricePreview.value = null
  createModalOpen.value = true
}

async function onHomestayChange(homestayId) {
  bookingForm.room_id = undefined
  pricePreview.value = null
  if (homestayId) {
    const res = await getRooms({ homestay_id: homestayId })
    availableRooms.value = res
  } else {
    availableRooms.value = []
  }
}

function onRoomChange() {
  pricePreview.value = null
  calculatePricePreview()
}

async function calculatePricePreview() {
  if (!bookingForm.room_id || !bookingForm.check_in_date || !bookingForm.check_out_date || !bookingForm.guest_count) {
    pricePreview.value = null
    return
  }
  
  try {
    const res = await calculatePrice({
      room_id: bookingForm.room_id,
      check_in_date: dayjs(bookingForm.check_in_date).format('YYYY-MM-DD'),
      check_out_date: dayjs(bookingForm.check_out_date).format('YYYY-MM-DD'),
      guest_count: bookingForm.guest_count
    })
    pricePreview.value = res
  } catch (e) {
    pricePreview.value = null
  }
}

async function submitBooking() {
  if (!bookingForm.homestay_id || !bookingForm.room_id || !bookingForm.check_in_date || !bookingForm.check_out_date || !bookingForm.guest_name || !bookingForm.guest_phone || !bookingForm.guest_count) {
    message.warning('请填写完整信息')
    return
  }
  
  if (!bookingForm.guest_phone.match(/^1[3-9]\d{9}$/)) {
    message.warning('请输入正确的手机号码')
    return
  }
  
  if (selectedRoom.value && bookingForm.guest_count > selectedRoom.value.max_guests) {
    message.warning(`入住人数不能超过房间最大容纳人数 ${selectedRoom.value.max_guests} 人`)
    return
  }
  
  submitting.value = true
  try {
    await createBooking({
      room_id: bookingForm.room_id,
      check_in_date: dayjs(bookingForm.check_in_date).format('YYYY-MM-DD'),
      check_out_date: dayjs(bookingForm.check_out_date).format('YYYY-MM-DD'),
      guest_name: bookingForm.guest_name,
      guest_phone: bookingForm.guest_phone,
      guest_count: bookingForm.guest_count,
      special_requests: bookingForm.special_requests || undefined
    })
    message.success('预订提交成功，等待民宿主确认')
    createModalOpen.value = false
    loadBookings()
  } finally {
    submitting.value = false
  }
}

const columns = [
  { title: '预订ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '住客姓名', dataIndex: 'guest_name', key: 'guest_name', width: 100 },
  { title: '联系电话', dataIndex: 'guest_phone', key: 'guest_phone', width: 130 },
  { title: '民宿', dataIndex: 'homestay_name', key: 'homestay_name', width: 120 },
  { title: '房间', dataIndex: 'room_name', key: 'room_name', width: 120 },
  { title: '入住日期', key: 'dates', width: 200 },
  { title: '入住人数', dataIndex: 'guest_count', key: 'guest_count', width: 80 },
  { title: '总价', dataIndex: 'total_price', key: 'total_price', width: 100, customRender: ({ text }) => `¥${text}` },
  { title: '状态', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 200, fixed: 'right' }
]

function statusText(status) {
  const map = {
    pending: '待确认',
    confirmed: '已确认',
    checked_in: '已入住',
    checked_out: '已退房',
    cancelled: '已取消'
  }
  return map[status] || status
}

function statusColor(status) {
  const map = {
    pending: 'orange',
    confirmed: 'blue',
    checked_in: 'green',
    checked_out: 'purple',
    cancelled: 'red'
  }
  return map[status] || 'default'
}

function nights(record) {
  return dayjs(record.check_out_date).diff(dayjs(record.check_in_date), 'day')
}

function canManage(record) {
  if (auth.isAdmin) return true
  return record.homestay_id && record.homestay_host_id === auth.user?.id
}

function viewDetail(record) {
  router.push(`/bookings/${record.id}`)
}

function confirmBooking(record) {
  Modal.confirm({
    title: '确认预订',
    content: `确定要确认预订 #${record.id} 吗？`,
    onOk: async () => {
      await updateBookingStatus(record.id, { status: 'confirmed' })
      message.success('确认成功')
      loadBookings()
    }
  })
}

function rejectBooking(record) {
  currentBooking.value = record
  rejectReason.value = ''
  rejectModalOpen.value = true
}

async function submitReject() {
  if (!rejectReason.value) {
    message.warning('请输入拒绝原因')
    return
  }
  await updateBookingStatus(currentBooking.value.id, {
    status: 'cancelled',
    reject_reason: rejectReason.value
  })
  message.success('已拒绝')
  rejectModalOpen.value = false
  loadBookings()
}

function checkIn(record) {
  Modal.confirm({
    title: '办理入住',
    content: `确定为预订 #${record.id} 办理入住吗？`,
    onOk: async () => {
      await updateBookingStatus(record.id, { status: 'checked_in' })
      message.success('入住办理成功')
      loadBookings()
    }
  })
}

function checkOut(record) {
  Modal.confirm({
    title: '办理退房',
    content: `确定为预订 #${record.id} 办理退房吗？`,
    onOk: async () => {
      await updateBookingStatus(record.id, { status: 'checked_out' })
      message.success('退房办理成功')
      loadBookings()
    }
  })
}

function cancelBooking(record) {
  Modal.confirm({
    title: '取消预订',
    content: `确定要取消预订 #${record.id} 吗？`,
    onOk: async () => {
      await updateBookingStatus(record.id, { status: 'cancelled' })
      message.success('已取消')
      loadBookings()
    }
  })
}

async function loadBookings() {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    if (homestayFilter.value) params.homestay_id = homestayFilter.value
    const res = await getBookings(params)
    bookings.value = res
  } finally {
    loading.value = false
  }
}

async function loadHomestays() {
  const res = await getHomestays()
  allHomestays.value = res
  if (auth.isAdmin) {
    homestays.value = res
  }
}

onMounted(() => {
  loadHomestays()
  loadBookings()
})
</script>

<style scoped>
.bookings-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.bookings-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}

.bookings-page .header-actions {
  display: flex;
  gap: 10px;
}

.price-preview {
  background: #f9f9f9;
  padding: 16px;
  border-radius: 8px;
  margin-top: 8px;
}

.price-item {
  text-align: center;
  padding: 12px;
  background: #fff;
  border-radius: 6px;
}

.price-item .price-label {
  font-size: 13px;
  color: #999;
  margin-bottom: 8px;
}

.price-item .price-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.price-item.total .price-value {
  color: #fa8c16;
}

.price-preview h4 {
  margin: 0;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}
</style>
