<template>
  <div class="homestays-page">
    <div class="page-header">
      <h2>民宿管理</h2>
      <a-button type="primary" @click="openModal()">
        <template #icon><PlusOutlined /></template>
        新增民宿
      </a-button>
    </div>

    <a-table :columns="columns" :data-source="homestays" :loading="loading" row-key="id">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'rating'">
          <a-rate :value="record.avg_rating || 0" disabled allow-half style="font-size: 14px" />
          <span style="margin-left: 8px; color: #fa8c16">{{ record.avg_rating || '-' }}</span>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="openModal(record)">编辑</a-button>
          <a-divider type="vertical" />
          <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" :title="isEdit ? '编辑民宿' : '新增民宿'" @ok="submitForm" width="600px">
      <a-form :model="form" layout="vertical">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="民宿名称" required>
              <a-input v-model:value="form.name" placeholder="请输入民宿名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="房间数量">
              <a-input-number v-model:value="form.room_count" :min="1" style="width: 100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="联系电话" required>
              <a-input v-model:value="form.contact_phone" placeholder="请输入联系电话" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="民宿主">
              <a-select v-model:value="form.host_id" placeholder="选择民宿主" style="width: 100%">
                <a-select-option v-for="u in hosts" :key="u.id" :value="u.id">
                  {{ u.full_name || u.username }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="地址">
              <a-input v-model:value="form.address" placeholder="请输入地址" />
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="描述">
              <a-textarea v-model:value="form.description" :rows="3" placeholder="民宿介绍" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { getHomestays, createHomestay, updateHomestay, deleteHomestay } from '@/api/homestays'
import request from '@/utils/request'

const homestays = ref([])
const loading = ref(false)
const modalOpen = ref(false)
const isEdit = ref(false)
const hosts = ref([])
const form = reactive({
  id: null,
  name: '',
  address: '',
  room_count: 5,
  contact_phone: '',
  description: '',
  host_id: null
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '民宿名称', dataIndex: 'name', key: 'name' },
  { title: '地址', dataIndex: 'address', key: 'address' },
  { title: '房间数', dataIndex: 'room_count', key: 'room_count', width: 80 },
  { title: '联系电话', dataIndex: 'contact_phone', key: 'contact_phone', width: 130 },
  { title: '评分', key: 'rating', width: 180 },
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
      address: '',
      room_count: 5,
      contact_phone: '',
      description: '',
      host_id: null
    })
  }
  modalOpen.value = true
}

async function loadHosts() {
  try {
    const res = await request.get('/auth/users')
    hosts.value = res.filter(u => u.role === 'host')
  } catch (e) {}
}

async function submitForm() {
  if (!form.name || !form.contact_phone) {
    message.warning('请填写必填项')
    return
  }
  
  try {
    if (isEdit.value) {
      await updateHomestay(form.id, form)
      message.success('更新成功')
    } else {
      await createHomestay(form)
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
      await deleteHomestay(record.id)
      message.success('删除成功')
      loadData()
    }
  })
}

async function loadData() {
  loading.value = true
  try {
    const res = await getHomestays()
    homestays.value = res
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  loadHosts()
})
</script>

<style scoped>
.homestays-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.homestays-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}
</style>
