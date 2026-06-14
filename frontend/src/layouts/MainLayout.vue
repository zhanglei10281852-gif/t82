<template>
  <a-layout class="main-layout">
    <a-layout-sider v-model:collapsed="collapsed" theme="dark" :trigger="null" collapsible width="220">
      <div class="logo">
        <HomeOutlined v-if="collapsed" />
        <span v-else>乡村民宿管理</span>
      </div>
      <a-menu theme="dark" mode="inline" :selected-keys="[$route.name]" @click="handleMenuClick">
        <a-menu-item key="Dashboard">
          <template #icon><DashboardOutlined /></template>
          <span>仪表盘</span>
        </a-menu-item>
        <a-menu-item v-if="auth.isAdmin" key="Homestays">
          <template #icon><ShopOutlined /></template>
          <span>民宿管理</span>
        </a-menu-item>
        <a-menu-item key="Rooms">
          <template #icon><HomeOutlined /></template>
          <span>房间管理</span>
        </a-menu-item>
        <a-menu-item key="Bookings">
          <template #icon><CalendarOutlined /></template>
          <span>预订管理</span>
        </a-menu-item>
        <a-menu-item key="Calendar">
          <template #icon><TableOutlined /></template>
          <span>房态日历</span>
        </a-menu-item>
        <a-menu-item key="Stats">
          <template #icon><BarChartOutlined /></template>
          <span>营收统计</span>
        </a-menu-item>
        <a-menu-item key="Reviews">
          <template #icon><StarOutlined /></template>
          <span>评价管理</span>
        </a-menu-item>
        <a-menu-item v-if="auth.isAdmin" key="Holidays">
          <template #icon><GiftOutlined /></template>
          <span>节假日管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <div class="header-left">
          <a-button type="text" @click="collapsed = !collapsed">
            <MenuUnfoldOutlined v-if="collapsed" />
            <MenuFoldOutlined v-else />
          </a-button>
          <span class="page-title">{{ $route.meta.title || '' }}</span>
        </div>
        <div class="header-right">
          <a-dropdown>
            <span class="user-info">
              <UserOutlined />
              <span>{{ auth.user?.full_name || auth.user?.username }}</span>
              <DownOutlined />
            </span>
            <template #overlay>
              <a-menu>
                <a-menu-item key="role">
                  角色：{{ auth.isAdmin ? '管理员' : '民宿主' }}
                </a-menu-item>
                <a-menu-divider />
                <a-menu-item key="logout" @click="handleLogout">
                  <LogoutOutlined /> 退出登录
                </a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </a-layout-header>
      <a-layout-content class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  ShopOutlined,
  HomeOutlined,
  CalendarOutlined,
  TableOutlined,
  BarChartOutlined,
  StarOutlined,
  GiftOutlined,
  UserOutlined,
  DownOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const collapsed = ref(false)

function handleMenuClick({ key }) {
  router.push({ name: key })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.1);
}

.header {
  background: #fff;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
}

.content {
  margin: 16px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: calc(100vh - 64px - 32px);
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
