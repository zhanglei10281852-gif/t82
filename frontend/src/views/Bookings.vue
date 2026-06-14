<template>
  <div class="bookings-page">
    <div class="page-header">
      <h2>预订管理</h2>
      <div class="header-actions">
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { SearchOutlined } from '@ant-design/icons-vue'
import { getBookings, updateBookingStatus } from '@/api/bookings'
import { getHomestays } from '@/api/homestays'
import { useAuthStore } from '@/stores/auth'
import dayjs from 'dayjs'

const router = useRouter()
const auth = useAuthStore()
const bookings = ref([])
const loading = ref(false)
const statusFilter = ref(undefined)
const homestayFilter = ref(undefined)
const homestays = ref([])
const rejectModalOpen = ref(false)
const rejectReason = ref('')
const currentBooking = ref(null)

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
  if (auth.isAdmin) {
    const res = await getHomestays()
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
</style>
