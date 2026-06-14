<template>
  <div class="calendar-page">
    <div class="page-header">
      <h2>房态日历</h2>
      <div class="header-actions">
        <a-select v-if="auth.isAdmin" v-model:value="homestayId" style="width: 200px" @change="loadCalendar">
          <a-select-option v-for="h in homestays" :key="h.id" :value="h.id">
            {{ h.name }}
          </a-select-option>
        </a-select>
        <a-date-picker v-model:value="currentDate" picker="month" @change="loadCalendar" style="width: 160px" />
      </div>
    </div>

    <div class="legend">
      <span class="legend-item"><span class="legend-color available"></span>空闲</span>
      <span class="legend-item"><span class="legend-color booked"></span>已预订</span>
      <span class="legend-item"><span class="legend-color occupied"></span>已入住</span>
      <span class="legend-item"><span class="legend-color maintenance"></span>维护中</span>
    </div>

    <div class="calendar-container" v-loading="loading">
      <div class="calendar-header">
        <div class="room-col">房间</div>
        <div class="days-row">
          <div v-for="day in daysHeader" :key="day.date" class="day-header" :class="{ weekend: day.weekend }">
            <div class="day-num">{{ day.day }}</div>
            <div class="day-week">{{ day.week }}</div>
          </div>
        </div>
      </div>
      <div class="calendar-body">
        <div v-for="room in calendarData?.rooms || []" :key="room.room_id" class="room-row">
          <div class="room-col room-name" :title="room.room_name">{{ room.room_name }}</div>
          <div class="days-row">
            <div
              v-for="day in room.days"
              :key="day.date"
              class="day-cell"
              :class="day.status"
              @click="handleCellClick(room, day)"
            >
              <span v-if="day.booking_id" class="booking-id">#{{ day.booking_id }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <a-modal v-model:open="maintenanceModalOpen" title="设置维护" @ok="submitMaintenance">
      <a-form layout="vertical">
        <a-form-item label="房间">
          <span>{{ selectedRoom?.room_name }}</span>
        </a-form-item>
        <a-form-item label="开始日期">
          <a-date-picker v-model:value="maintenanceForm.start_date" style="width: 100%" />
        </a-form-item>
        <a-form-item label="结束日期">
          <a-date-picker v-model:value="maintenanceForm.end_date" style="width: 100%" />
        </a-form-item>
        <a-form-item label="原因">
          <a-input v-model:value="maintenanceForm.reason" placeholder="维护原因" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { getHomestays } from '@/api/homestays'
import { getHomestayCalendar } from '@/api/calendar'
import { createMaintenance } from '@/api/maintenance'
import dayjs from 'dayjs'

const auth = useAuthStore()
const homestays = ref([])
const homestayId = ref(null)
const currentDate = ref(dayjs())
const calendarData = ref(null)
const loading = ref(false)
const maintenanceModalOpen = ref(false)
const selectedRoom = ref(null)
const selectedDay = ref(null)
const maintenanceForm = ref({ start_date: null, end_date: null, reason: '' })

const daysHeader = computed(() => {
  if (!calendarData.value?.rooms?.[0]?.days) return []
  return calendarData.value.rooms[0].days.map(d => ({
    date: d.date,
    day: dayjs(d.date).date(),
    week: ['日', '一', '二', '三', '四', '五', '六'][dayjs(d.date).day()],
    weekend: dayjs(d.date).day() === 0 || dayjs(d.date).day() === 6
  }))
})

function handleCellClick(room, day) {
  if (day.status === 'available' && (auth.isAdmin || auth.isHost)) {
    selectedRoom.value = room
    selectedDay.value = day
    maintenanceForm.value = {
      start_date: dayjs(day.date),
      end_date: dayjs(day.date).add(1, 'day'),
      reason: ''
    }
    maintenanceModalOpen.value = true
  }
}

async function submitMaintenance() {
  if (!maintenanceForm.value.start_date || !maintenanceForm.value.end_date) {
    message.warning('请选择日期')
    return
  }
  try {
    await createMaintenance({
      room_id: selectedRoom.value.room_id,
      start_date: dayjs(maintenanceForm.value.start_date).format('YYYY-MM-DD'),
      end_date: dayjs(maintenanceForm.value.end_date).format('YYYY-MM-DD'),
      reason: maintenanceForm.value.reason
    })
    message.success('设置成功')
    maintenanceModalOpen.value = false
    loadCalendar()
  } catch (e) {}
}

async function loadCalendar() {
  if (!homestayId.value) return
  loading.value = true
  try {
    const res = await getHomestayCalendar(homestayId.value, {
      year: currentDate.value.year(),
      month: currentDate.value.month() + 1
    })
    calendarData.value = res
  } finally {
    loading.value = false
  }
}

async function loadHomestays() {
  const res = await getHomestays()
  homestays.value = res
  if (res.length > 0) {
    homestayId.value = res[0].id
    loadCalendar()
  }
}

onMounted(() => {
  loadHomestays()
})
</script>

<style scoped>
.calendar-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.calendar-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}

.calendar-page .header-actions {
  display: flex;
  gap: 10px;
}

.legend {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.legend-color.available { background: #52c41a; }
.legend-color.booked { background: #1890ff; }
.legend-color.occupied { background: #fa8c16; }
.legend-color.maintenance { background: #ff4d4f; }

.calendar-container {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: auto;
}

.calendar-header {
  display: flex;
  position: sticky;
  top: 0;
  z-index: 2;
  background: #fafafa;
}

.room-col {
  width: 120px;
  min-width: 120px;
  padding: 10px;
  border-right: 1px solid #e8e8e8;
  border-bottom: 1px solid #e8e8e8;
  font-weight: 500;
  text-align: center;
  background: #fafafa;
  position: sticky;
  left: 0;
  z-index: 3;
}

.room-name {
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.days-row {
  display: flex;
  flex: 1;
}

.day-header {
  width: 40px;
  min-width: 40px;
  padding: 8px 4px;
  text-align: center;
  border-right: 1px solid #e8e8e8;
  border-bottom: 1px solid #e8e8e8;
  font-size: 12px;
  color: #666;
}

.day-header.weekend {
  color: #ff4d4f;
}

.day-num {
  font-size: 14px;
  font-weight: 500;
}

.day-week {
  font-size: 11px;
  margin-top: 2px;
}

.calendar-body {
  max-height: 500px;
  overflow-y: auto;
}

.room-row {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
}

.room-row:last-child {
  border-bottom: none;
}

.day-cell {
  width: 40px;
  min-width: 40px;
  height: 36px;
  border-right: 1px solid #f0f0f0;
  cursor: pointer;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: transparent;
}

.day-cell.available { background: #f6ffed; }
.day-cell.booked { background: #e6f7ff; }
.day-cell.occupied { background: #fff7e6; }
.day-cell.maintenance { background: #fff1f0; }

.day-cell:hover {
  filter: brightness(0.95);
}

.booking-id {
  color: #1890ff;
  font-size: 10px;
}
</style>
