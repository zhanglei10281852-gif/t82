<template>
  <div class="dashboard">
    <div class="stats-cards">
      <a-row :gutter="16">
        <a-col :span="6">
          <a-card class="stat-card revenue">
            <div class="stat-content">
              <div class="stat-label">总营收</div>
              <div class="stat-value">¥{{ formatNumber(stats.total_revenue) }}</div>
              <div class="stat-desc">本月累计</div>
            </div>
            <div class="stat-icon"><DollarOutlined /></div>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card booking">
            <div class="stat-content">
              <div class="stat-label">预订数量</div>
              <div class="stat-value">{{ stats.total_bookings }}</div>
              <div class="stat-desc">本月预订</div>
            </div>
            <div class="stat-icon"><CalendarOutlined /></div>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card occupancy">
            <div class="stat-content">
              <div class="stat-label">入住率</div>
              <div class="stat-value">{{ stats.occupancy_rate }}%</div>
              <div class="stat-desc">平均入住率</div>
            </div>
            <div class="stat-icon"><HomeOutlined /></div>
          </a-card>
        </a-col>
        <a-col :span="6">
          <a-card class="stat-card adr">
            <div class="stat-content">
              <div class="stat-label">平均房价</div>
              <div class="stat-value">¥{{ formatNumber(stats.avg_daily_rate) }}</div>
              <div class="stat-desc">ADR</div>
            </div>
            <div class="stat-icon"><LineChartOutlined /></div>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <a-row :gutter="16" style="margin-top: 16px">
      <a-col :span="14">
        <a-card title="各民宿营收排名">
          <v-chart :option="rankingChart" autoresize style="height: 350px" />
        </a-card>
      </a-col>
      <a-col :span="10">
        <a-card title="民宿评分排行">
          <div v-for="(item, index) in ranking" :key="item.homestay_id" class="ranking-item">
            <span class="rank-num" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
            <span class="rank-name">{{ item.homestay_name }}</span>
            <a-rate :value="item.avg_rating" disabled allow-half style="font-size: 14px" />
            <span class="rank-score">{{ item.avg_rating }}</span>
            <span class="rank-count">({{ item.review_count }}条评价)</span>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-card title="本月预订量趋势" style="margin-top: 16px">
      <v-chart :option="trendChart" autoresize style="height: 300px" />
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getDashboardStats, getHomestayRanking } from '@/api/stats'
import {
  DollarOutlined,
  CalendarOutlined,
  HomeOutlined,
  LineChartOutlined
} from '@ant-design/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import dayjs from 'dayjs'

use([
  CanvasRenderer,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const auth = useAuthStore()
const stats = ref({
  total_revenue: 0,
  total_bookings: 0,
  occupancy_rate: 0,
  avg_daily_rate: 0,
  homestay_revenue_ranking: [],
  monthly_booking_trend: []
})
const ranking = ref([])

const rankingChart = computed(() => ({
  tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'value',
    axisLabel: { formatter: value => '¥' + value }
  },
  yAxis: {
    type: 'category',
    data: stats.value.homestay_revenue_ranking.map(r => r.homestay_name).reverse()
  },
  series: [{
    name: '营收',
    type: 'bar',
    data: stats.value.homestay_revenue_ranking.map(r => r.revenue).reverse(),
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 1, y2: 0,
        colorStops: [
          { offset: 0, color: '#667eea' },
          { offset: 1, color: '#764ba2' }
        ]
      },
      borderRadius: [0, 4, 4, 0]
    },
    label: {
      show: true,
      position: 'right',
      formatter: params => '¥' + params.value
    }
  }]
}))

const trendChart = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['预订数量', '营收'] },
  grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: stats.value.monthly_booking_trend.map(t => t.month.slice(5))
  },
  yAxis: [
    { type: 'value', name: '预订数' },
    { type: 'value', name: '营收', axisLabel: { formatter: '¥{value}' } }
  ],
  series: [
    {
      name: '预订数量',
      type: 'bar',
      data: stats.value.monthly_booking_trend.map(t => t.booking_count),
      itemStyle: { color: '#667eea', borderRadius: [4, 4, 0, 0] }
    },
    {
      name: '营收',
      type: 'line',
      yAxisIndex: 1,
      data: stats.value.monthly_booking_trend.map(t => t.revenue),
      smooth: true,
      itemStyle: { color: '#f093fb' },
      lineStyle: { width: 3 }
    }
  ]
}))

function formatNumber(num) {
  return num?.toLocaleString() || 0
}

async function loadData() {
  const now = dayjs()
  const res = await getDashboardStats({ year: now.year(), month: now.month() + 1 })
  stats.value = res
  
  const rankRes = await getHomestayRanking()
  ranking.value = rankRes
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  border-radius: 8px;
  overflow: hidden;
}

.stat-card :deep(.ant-card-body) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.stat-desc {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.revenue .stat-icon { background: linear-gradient(135deg, #667eea, #764ba2); }
.booking .stat-icon { background: linear-gradient(135deg, #f093fb, #f5576c); }
.occupancy .stat-icon { background: linear-gradient(135deg, #4facfe, #00f2fe); }
.adr .stat-icon { background: linear-gradient(135deg, #43e97b, #38f9d7); }

.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
  gap: 10px;
}

.ranking-item:last-child {
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

.rank-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.rank-score {
  font-weight: bold;
  color: #fa8c16;
  font-size: 14px;
}

.rank-count {
  font-size: 12px;
  color: #999;
}
</style>
