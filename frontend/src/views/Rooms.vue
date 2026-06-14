<template>
  <div class="rooms-page">
    <div class="page-header">
      <h2>房间管理</h2>
      <div class="header-actions">
        <a-select v-if="auth.isAdmin" v-model:value="homestayFilter" placeholder="全部民宿" style="width: 180px" allow-clear @change="loadData">
          <a-select-option v-for="h in homestays" :key="h.id" :value="h.id">
            {{ h.name }}
          </a-select-option>
        </a-select>
        <a-button type="primary" @click="openModal()" v-if="auth.isAdmin">
          <template #icon><PlusOutlined /></template>
          新增房间
        </a-button>
      </div>
    </div>

    <a-table :columns="columns" :data-source="rooms" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'room_type'">
          <a-tag>{{ record.room_type }}</a-tag>
        </template>
        <template v-else-if="column.key === 'price'">
          <span style="color: #f5222d; font-weight: 500">¥{{ record.base_price }}</span>
        </template>
        <template v-else-if="column.key === 'rating'">
          <a-rate :value="record.avg_rating || 0" disabled allow-half style="font-size: 12px" />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="openModal(record)">编辑</a-button>
          <a-divider type="vertical" />
          <a-button type="link" danger @click="handleDelete(record)" v-if="auth.isAdmin">删除</a-button>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="isEdit ? '编辑房间' : '新增房间'" @ok="submitForm" width="500px">
      <a-form :model="form" layout="vertical">
        <a-form-item label="所属民宿" required v-if="!isEdit">
          <a-select v-model:value="form.homestay_id" placeholder="选择民宿" style="width: 100%">
            <a-select-option v-for="h in homestays" :key="h.id" :value="h.id">
              {{ h.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="房间名称" required>
          <a-input v-model:value="form.name" placeholder="请输入房间名称" />
        </a-form-item>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="房型" required>
              <a-select v-model:value="form.room_type" style="width: 100%">
                <a-select-option value="大床房">大床房</a-select-option>
                <a-select-option value="双床房">双床房</a-select-option>
                <a-select-option value="家庭套房">家庭套房</a-select-option>
                <a-select-option value="豪华大床房">豪华大床房</a-select-option>
                <a-select-option value="行政套房">行政套房</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="面积(㎡)">
              <a-input-number v-model:value="form.area" :min="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="基础价格(元)" required>
              <a-input-number v-model:value="form.base_price" :min="0" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="最多入住人数" required>
              <a-input-number v-model:value="form.max_guests" :min="1" style="width: 100%" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { getRooms, createRoom, updateRoom, deleteRoom } from '@/api/rooms'
import { getHomestays } from '@/api/homestays'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const rooms = ref([])
const homestays = ref([])
const homestayFilter = ref(undefined)
const loading = ref(false)
const modalOpen = ref(false)
const isEdit = ref(false)

const form = reactive({
  id: null,
  name: '',
  room_type: '大床房',
  area: 25,
  base_price: 200,
  max_guests: 2,
  homestay_id: null
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '房间名称', dataIndex: 'name', key: 'name' },
  { title: '民宿', dataIndex: 'homestay_name', key: 'homestay_name' },
  { title: '房型', key: 'room_type', width: 100 },
  { title: '面积', dataIndex: 'area', key: 'area', width: 80, customRender: ({ text }) => `${text}㎡` },
  { title: '基础价格', key: 'price', width: 100 },
  { title: '最多入住', dataIndex: 'max_guests', key: 'max_guests', width: 90, customRender: ({ text }) => `${text}人` },
  { title: '评分', key: 'rating', width: 120 },
  { title: '操作', key: 'action', width: 150, fixed: 'right' }
]

function openModal(record) {
  if (record) {
    isEdit.value = true
    Object.assign(form, record)
  } else {
    isEdit.value = false
    Object.assign(form, {
      id: null,
      name: '',
      room_type: '大床房',
      area: 25,
      base_price: 200,
      max_guests: 2,
      homestay_id: homestayFilter.value || (homestays.value[0]?.id)
    })
  }
  modalOpen.value = true
}

async function submitForm() {
  if (!form.name || !form.room_type || !form.base_price || !form.max_guests) {
    message.warning('请填写必填项')
    return
  }
  if (!form.homestay_id) {
    message.warning('请选择民宿')
    return
  }
  
  try {
    if (isEdit.value) {
      await updateRoom(form.id, form)
      message.success('更新成功')
    } else {
      await createRoom(form)
      message.success('创建成功')
    }
    modalOpen.value = false
    loadData()
  } catch (e) {}
}

function handleDelete(record) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除「${record.name}」吗？`,
    onOk: async () => {
      await deleteRoom(record.id)
      message.success('删除成功')
      loadData()
    }
  })
}

async function loadData() {
  loading.value = true
  try {
    const params = {}
    if (homestayFilter.value) params.homestay_id = homestayFilter.value
    const res = await getRooms(params)
    rooms.value = res
  } finally {
    loading.value = false
  }
}

async function loadHomestays() {
  const res = await getHomestays()
  homestays.value = res
  if (auth.isHost && res.length > 0) {
    homestayFilter.value = res[0].id
  }
}

onMounted(() => {
  loadHomestays().then(() => loadData())
})
</script>

<style scoped>
.rooms-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.rooms-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}

.rooms-page .header-actions {
  display: flex;
  gap: 10px;
}
</style>
