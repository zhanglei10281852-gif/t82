<template>
  <div class="holidays-page">
    <div class="page-header">
      <h2>节假日管理</h2>
      <a-button type="primary" @click="openModal()">
        <template #icon><PlusOutlined /></template>
        新增节假日
      </a-button>
    </div>

    <a-row :gutter="16">
      <a-col :span="6">
        <a-select v-model:value="yearFilter" style="width: 100%" @change="loadData">
          <a-select-option :value="2024">2024年</a-select-option>
          <a-select-option :value="2025">2025年</a-select-option>
          <a-select-option :value="2026">2026年</a-select-option>
        </a-select>
      </a-col>
    </a-row>

    <a-table :columns="columns" :data-source="holidays" :loading="loading" row-key="id" style="margin-top: 16px">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
        </template>
      </template>
    </a-table>

    <a-modal v-model:open="modalOpen" title="新增节假日" @ok="submitForm" width="400px">
      <a-form :model="form" layout="vertical">
        <a-form-item label="日期" required>
          <a-date-picker v-model:value="form.date" style="width: 100%" />
        </a-form-item>
        <a-form-item label="节假日名称" required>
          <a-input v-model:value="form.name" placeholder="如：春节、国庆节" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { getHolidays, createHoliday, deleteHoliday } from '@/api/holidays'
import dayjs from 'dayjs'

const holidays = ref([])
const loading = ref(false)
const modalOpen = ref(false)
const yearFilter = ref(new Date().getFullYear())

const form = reactive({
  date: null,
  name: ''
})

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: '日期', dataIndex: 'date', key: 'date', width: 140 },
  { title: '节假日名称', dataIndex: 'name', key: 'name' },
  { title: '操作', key: 'action', width: 100 }
]

function openModal() {
  form.date = null
  form.name = ''
  modalOpen.value = true
}

async function submitForm() {
  if (!form.date || !form.name) {
    message.warning('请填写完整信息')
    return
  }
  
  try {
    await createHoliday({
      date: dayjs(form.date).format('YYYY-MM-DD'),
      name: form.name
    })
    message.success('添加成功')
    modalOpen.value = false
    loadData()
  } catch (e) {}
}

function handleDelete(record) {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除「${record.name} - ${record.date}」吗？`,
    onOk: async () => {
      await deleteHoliday(record.id)
      message.success('删除成功')
      loadData()
    }
  })
}

async function loadData() {
  loading.value = true
  try {
    const res = await getHolidays({ year: yearFilter.value })
    holidays.value = res
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.holidays-page .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.holidays-page .page-header h2 {
  margin: 0;
  font-size: 20px;
}
</style>
