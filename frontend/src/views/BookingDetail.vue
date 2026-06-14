<template>
  <div class="booking-detail">
    <a-page-header title="预订详情" @back="$router.back()">
      <template #extra>
        <a-tag :color="statusColor(booking.status)">
          {{ statusText(booking.status) }}
        </a-tag>
      </template>
    </a-page-header>

    <a-row :gutter="24">
      <a-col :span="16">
        <a-card title="预订信息" style="margin-top: 16px">
          <a-descriptions :column="2" bordered>
            <a-descriptions-item label="预订编号">#{{ booking.id }}</a-descriptions-item>
            <a-descriptions-item label="预订时间">{{ booking.created_at }}</a-descriptions-item>
            <a-descriptions-item label="住客姓名">{{ booking.guest_name }}</a-descriptions-item>
            <a-descriptions-item label="联系电话">{{ booking.guest_phone }}</a-descriptions-item>
            <a-descriptions-item label="民宿">{{ booking.homestay_name }}</a-descriptions-item>
            <a-descriptions-item label="房间">{{ booking.room_name }}</a-descriptions-item>
            <a-descriptions-item label="入住日期">{{ booking.check_in_date }}</a-descriptions-item>
            <a-descriptions-item label="退房日期">{{ booking.check_out_date }}</a-descriptions-item>
            <a-descriptions-item label="入住人数">{{ booking.guest_count }}人</a-descriptions-item>
            <a-descriptions-item label="总价格">
              <span style="color: #f5222d; font-size: 18px; font-weight: bold">¥{{ booking.total_price }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="特殊需求" :span="2">
              {{ booking.special_requests || '无' }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="状态记录" style="margin-top: 16px">
          <a-steps direction="vertical" size="small" :current="currentStep">
            <a-step title="提交预订" :description="booking.created_at" />
            <a-step title="已确认" description="民宿主确认预订" />
            <a-step title="已入住" :description="booking.actual_check_in" />
            <a-step title="已退房" :description="booking.actual_check_out" />
          </a-steps>
          <div v-if="booking.reject_reason" style="margin-top: 16px; color: #ff4d4f">
            <strong>拒绝原因：</strong>{{ booking.reject_reason }}
          </div>
        </a-card>

        <a-card v-if="booking.status === 'checked_out' && !hasReview" title="评价订单" style="margin-top: 16px">
          <a-form :model="reviewForm" layout="vertical">
            <a-form-item label="评分">
              <a-rate v-model:value="reviewForm.rating" />
            </a-form-item>
            <a-form-item label="评价内容">
              <a-textarea v-model:value="reviewForm.content" :rows="4" placeholder="说说您的入住体验..." />
            </a-form-item>
            <a-button type="primary" @click="submitReview">提交评价</a-button>
          </a-form>
        </a-card>

        <a-card v-if="review" title="住客评价" style="margin-top: 16px">
          <div class="review-header">
            <span class="review-guest">{{ review.guest_name }}</span>
            <a-rate :value="review.rating" disabled style="font-size: 16px" />
            <span class="review-score">{{ review.rating }}分</span>
          </div>
          <div class="review-content">{{ review.content || '无评价内容' }}</div>
          <div class="review-time">{{ review.created_at }}</div>
        </a-card>
      </a-col>

      <a-col :span="8">
        <a-card title="操作" style="margin-top: 16px">
          <template v-if="canManage && booking.status === 'pending'">
            <a-button type="primary" block style="margin-bottom: 10px" @click="confirmBooking">
              <CheckOutlined /> 确认预订
            </a-button>
            <a-button danger block @click="rejectBooking">
              <CloseOutlined /> 拒绝预订
            </a-button>
          </template>
          <template v-else-if="canManage && booking.status === 'confirmed'">
            <a-button type="primary" block style="margin-bottom: 10px" @click="checkIn">
              <LoginOutlined /> 办理入住
            </a-button>
            <a-button danger block @click="cancelBooking">
              <StopOutlined /> 取消预订
            </a-button>
          </template>
          <template v-else-if="canManage && booking.status === 'checked_in'">
            <a-button type="primary" block @click="checkOut">
              <LogoutOutlined /> 办理退房
            </a-button>
          </template>
          <a-empty v-else description="无可用操作" />
        </a-card>

        <a-card title="价格明细" style="margin-top: 16px">
          <a-list size="small">
            <a-list-item v-for="(item, index) in priceBreakdown" :key="index">
              <span>{{ item.date }}</span>
              <span>¥{{ item.price }}</span>
            </a-list-item>
          </a-list>
          <a-divider style="margin: 12px 0" />
          <div class="price-summary">
            <span>合计</span>
            <span class="total">¥{{ booking.total_price }}</span>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-modal v-model:open="rejectModalOpen" title="拒绝预订" @ok="submitReject">
      <a-textarea v-model:value="rejectReason" placeholder="请输入拒绝原因" :rows="4" />
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  CheckOutlined,
  CloseOutlined,
  LoginOutlined,
  LogoutOutlined,
  StopOutlined
} from '@ant-design/icons-vue'
import { getBooking, updateBookingStatus, calculatePrice } from '@/api/bookings'
import { getReviews, createReview } from '@/api/reviews'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const booking = ref({})
const review = ref(null)
const hasReview = ref(false)
const rejectModalOpen = ref(false)
const rejectReason = ref('')
const priceBreakdown = ref([])
const reviewForm = ref({ rating: 5, content: '' })

const canManage = computed(() => {
  if (auth.isAdmin) return true
  return booking.value.homestay_id && true
})

const currentStep = computed(() => {
  const map = {
    pending: 0,
    confirmed: 1,
    checked_in: 2,
    checked_out: 3,
    cancelled: 0
  }
  return map[booking.value.status] || 0
})

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

function confirmBooking() {
  Modal.confirm({
    title: '确认预订',
    content: '确定要确认该预订吗？',
    onOk: async () => {
      await updateBookingStatus(route.params.id, { status: 'confirmed' })
      message.success('确认成功')
      loadBooking()
    }
  })
}

function rejectBooking() {
  rejectReason.value = ''
  rejectModalOpen.value = true
}

async function submitReject() {
  if (!rejectReason.value) {
    message.warning('请输入拒绝原因')
    return
  }
  await updateBookingStatus(route.params.id, {
    status: 'cancelled',
    reject_reason: rejectReason.value
  })
  message.success('已拒绝')
  rejectModalOpen.value = false
  loadBooking()
}

function checkIn() {
  Modal.confirm({
    title: '办理入住',
    content: '确定为该预订办理入住吗？',
    onOk: async () => {
      await updateBookingStatus(route.params.id, { status: 'checked_in' })
      message.success('入住办理成功')
      loadBooking()
    }
  })
}

function checkOut() {
  Modal.confirm({
    title: '办理退房',
    content: '确定为该预订办理退房吗？',
    onOk: async () => {
      await updateBookingStatus(route.params.id, { status: 'checked_out' })
      message.success('退房办理成功')
      loadBooking()
    }
  })
}

function cancelBooking() {
  Modal.confirm({
    title: '取消预订',
    content: '确定要取消该预订吗？',
    onOk: async () => {
      await updateBookingStatus(route.params.id, { status: 'cancelled' })
      message.success('已取消')
      loadBooking()
    }
  })
}

async function submitReview() {
  if (!reviewForm.value.rating) {
    message.warning('请选择评分')
    return
  }
  await createReview({
    booking_id: booking.value.id,
    rating: reviewForm.value.rating,
    content: reviewForm.value.content
  })
  message.success('评价提交成功')
  loadReviews()
}

async function loadBooking() {
  const res = await getBooking(route.params.id)
  booking.value = res
  
  if (res.check_in_date && res.check_out_date && res.room_id) {
    try {
      const priceRes = await calculatePrice({
        room_id: res.room_id,
        check_in_date: res.check_in_date,
        check_out_date: res.check_out_date
      })
      priceBreakdown.value = priceRes.nightly_prices || []
    } catch (e) {}
  }
}

async function loadReviews() {
  try {
    const res = await getReviews({ room_id: booking.value.room_id })
    const myReview = res.find(r => r.booking_id === booking.value.id)
    if (myReview) {
      review.value = myReview
      hasReview.value = true
    } else {
      hasReview.value = false
    }
  } catch (e) {}
}

onMounted(() => {
  loadBooking().then(() => {
    if (booking.value.status === 'checked_out') {
      loadReviews()
    }
  })
})
</script>

<style scoped>
.booking-detail {
  padding: 0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.review-guest {
  font-weight: 500;
  color: #333;
}

.review-score {
  color: #fa8c16;
  font-weight: bold;
}

.review-content {
  color: #666;
  line-height: 1.6;
  margin-bottom: 8px;
}

.review-time {
  font-size: 12px;
  color: #999;
}

.price-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}

.price-summary .total {
  font-size: 20px;
  font-weight: bold;
  color: #f5222d;
}
</style>
