<template>
  <div class="stats-page">
    <div class="page-header">
      <h2>营收统计</h2>
      <div class="header-actions">
        <a-select v-if="auth.isAdmin" v-model:value="homestayId" placeholder="全部民宿" style="width: 180px" allow-clear @change="loadStats">
          <a-select-option v-for="h in homestays" :key="h.id" :value="h.id">
            {{ h.name }}
          </a-select-option>
        </a-select>
        <a-date-picker v-model:value="currentDate" picker="month" @change="loadStats" style="width: 160px" />
      </div>
    </div>

    <a-row :gutter="16" v-if="homestayStats">
      <a-col :span="6">
        <a-card class="stat-card">
          <div class="stat-label">总营收</div>
          <div class="stat-value revenue">¥{{ formatNumber(homestayStats.total_revenue) }}</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <div class="stat-label">入住率</div>
          <div class="stat-value occupancy">{{ homestayStats.occupancy_rate }}%</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <div class="stat-label">平均房价</div>
          <div class="stat-value adr">¥{{ formatNumber(homestayStats.avg_daily_rate) }}</div>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card class="stat-card">
          <div class="stat-label">已售间夜</div>
          <div class="stat-value nights">{{ homestayStats.sold_nights }} / {{ homestayStats.available_nights }}</div>
        </a-card>
      </a-col>
    </a-row>

    <a-card title="各房型销售占比" style="margin-top: 16px" v-if="homestayStats">
      <a-row :gutter="16">
        <a-col :span="14">
          <v-chart :option="roomTypeChart" autoresize style="height: 300px" />
        </a-col>
        <a-col :span="10">
          <a-table
            :columns="roomTypeColumns"
            :data-source="homestayStats.room_type_stats"
            :pagination="false"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'percentage'">
                {{ record.percentage.toFixed(1) }}%
              </template>
              <template v-else-if="column.key === 'revenue'">
                ¥{{ record.revenue.toFixed(2) }}
              </template>
            </template>
          </a-table>
        </a-col>
      </a-row>
    </a-card>

    <a-card v-if="auth.isAdmin" title="各民宿营收对比" style="margin-top: 16px">
      <v-chart :option="comparisonChart" autoresize style="height: 350px" />
    </a-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { getHomestays } from '@/api/homestays'
import { getHomestayRevenue, getDashboardStats } from '@/api/stats'
import dayjs from 'dayjs'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const auth = useAuthStore()
const homestays = ref([])
const homestayId = ref(null)
const currentDate = ref(dayjs())
const homestayStats = ref(null)
const allStats = ref([])

const roomTypeColumns = [
  { title: '房型', dataIndex: 'room_type', key: 'room_type' },
  { title: '间夜数', dataIndex: 'nights', key: 'nights' },
  { title: '营收', dataIndex: 'revenue', key: 'revenue' },
  { title: '占比', key: 'percentage' }
]

const roomTypeChart = computed(() => {
  const data = homestayStats.value?.room_type_stats || []
  return {
    tooltip: { trigger: 'item', formatter: '{b}: ¥{c} ({d}%)' },
    legend: { orient: 'vertical', left: 'left' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: data.map(d => ({ name: d.room_type, value: d.revenue })),
      label: { formatter: '{b}\n{d}%' },
      itemStyle: {
        borderRadius: 4,
        borderColor: '#fff',
        borderWidth: 2
      }
    }],
    color: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a', '#fee140']
  }
})

const comparisonChart = computed(() => {
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: allStats.value.map(s => s.homestay_name)
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: '¥{value}' }
    },
    series: [{
      name: '营收',
      type: 'bar',
      data: allStats.value.map(s => s.total_revenue),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#667eea' },
            { offset: 1, color: '#764ba2' }
          ]
        },
        borderRadius: [4, 4, 0, 0]
      },
      barWidth: '50%',
      label: {
        show: true,
        position: 'top',
        formatter: params => '¥' + params.value.toFixed(0)
      }
    }]
  }
})

function formatNumber(num) {
  return num?.toLocaleString() || 0
}

async function loadStats() {
  if (!homestayId.value) {
    if (auth.isAdmin) {
      loadAllStats()
    }
    return
  }
  
  const res = await getHomestayRevenue(homestayId.value, {
    year: currentDate.value.year(),
    month: currentDate.value.month() + 1
  })
  homestayStats.value = res
}

async function loadAllStats() {
  const year = currentDate.value.year()
  const month = currentDate.value.month() + 1
  
  const results = []
  for (const hs of homestays.value) {
    try {
      const res = await getHomestayRevenue(hs.id, { year, month })
      results.push(res)
    } catch (e) {}
  }
  allStats.value = results.sort((a, b) => b.total_revenue - a.total_revenue)
  
  if (results.length > 0) {
    homestayStats.value = results[0]
    homestayId.value = results[0].homestay_id
  }
}

async function loadHomestays() {
  const res = await getHomestays()
  homestays.value = res
  if (res.length > 0 && auth.isHost) {
    homestayId.value = res[0].id
  }
  loadStats()
}

onMounted(() => {
  loadHomestays()
})
</script>

<style scoped>
.stats-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.stats-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}

.stats-page .header-actions {
  display: flex;
  gap: 10px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-value.revenue { color: #667eea; }
.stat-value.occupancy { color: #52c41a; }
.stat-value.adr { color: #fa8c16; }
.stat-value.nights { color: #1890ff; font-size: 22px; }
</style>
