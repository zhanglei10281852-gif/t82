<template>
  <div class="reviews-page">
    <div class="page-header">
      <h2>评价管理</h2>
      <div class="header-actions">
        <a-select v-if="auth.isAdmin" v-model:value="homestayFilter" placeholder="全部民宿" style="width: 180px" allow-clear @change="loadData">
          <a-select-option v-for="h in homestays" :key="h.id" :value="h.id">
            {{ h.name }}
          </a-select-option>
        </a-select>
      </div>
    </div>

    <a-row :gutter="16">
      <a-col :span="8">
        <a-card title="民宿评分排行">
          <div v-for="(item, index) in ranking" :key="item.homestay_id" class="rank-item" @click="selectHomestay(item.homestay_id)">
            <span class="rank-num" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            <div class="rank-info">
              <div class="rank-name">{{ item.homestay_name }}</div>
              <div class="rank-rate">
                <a-rate :value="item.avg_rating" disabled allow-half style="font-size: 14px" />
                <span class="rank-score">{{ item.avg_rating }}分</span>
                <span class="rank-count">{{ item.review_count }}条</span>
              </div>
            </div>
          </div>
        </a-card>
      </a-col>
      <a-col :span="16">
        <a-card title="评价列表">
          <div v-for="review in reviews" :key="review.id" class="review-item">
            <div class="review-header">
              <div class="review-user">
                <div class="avatar">{{ review.guest_name?.charAt(0) || '用' }}</div>
                <div>
                  <div class="review-name">{{ review.guest_name || '匿名用户' }}</div>
                  <div class="review-time">{{ review.created_at }}</div>
                </div>
              </div>
              <a-rate :value="review.rating" disabled style="font-size: 16px" />
            </div>
            <div class="review-body">
              <div class="review-room">房间：{{ review.room_name }} · {{ review.homestay_name }}</div>
              <div class="review-content">{{ review.content || '用户未填写评价内容' }}</div>
            </div>
          </div>
          <a-empty v-if="!reviews.length" description="暂无评价" />
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getReviews } from '@/api/reviews'
import { getHomestays } from '@/api/homestays'
import { getHomestayRanking } from '@/api/stats'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const reviews = ref([])
const homestays = ref([])
const ranking = ref([])
const homestayFilter = ref(undefined)

function selectHomestay(id) {
  homestayFilter.value = id
  loadData()
}

async function loadData() {
  const params = {}
  if (homestayFilter.value) params.homestay_id = homestayFilter.value
  const res = await getReviews(params)
  reviews.value = res
}

async function loadRanking() {
  const res = await getHomestayRanking()
  ranking.value = res
}

async function loadHomestays() {
  if (auth.isAdmin) {
    const res = await getHomestays()
    homestays.value = res
  }
}

onMounted(() => {
  loadHomestays()
  loadData()
  loadRanking()
})
</script>

<style scoped>
.reviews-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.reviews-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}

.rank-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.rank-item:hover {
  background: #f5f5f5;
  margin: 0 -12px;
  padding: 12px;
  border-radius: 4px;
}

.rank-item:last-child {
  border-bottom: none;
}

.rank-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #fff;
  font-size: 12px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.rank-1 { background: #ffc107; }
.rank-2 { background: #9e9e9e; }
.rank-3 { background: #cd7f32; }

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.rank-rate {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.rank-score {
  color: #fa8c16;
  font-weight: bold;
}

.rank-count {
  color: #999;
}

.review-item {
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.review-item:last-child {
  border-bottom: none;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.review-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.review-name {
  font-weight: 500;
  color: #333;
}

.review-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.review-room {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
}

.review-content {
  color: #555;
  line-height: 1.6;
}
</style>
