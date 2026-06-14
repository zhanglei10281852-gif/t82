import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { guest: true }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'homestays',
        name: 'Homestays',
        component: () => import('@/views/Homestays.vue'),
        meta: { title: '民宿管理', roles: ['admin'] }
      },
      {
        path: 'rooms',
        name: 'Rooms',
        component: () => import('@/views/Rooms.vue'),
        meta: { title: '房间管理' }
      },
      {
        path: 'bookings',
        name: 'Bookings',
        component: () => import('@/views/Bookings.vue'),
        meta: { title: '预订管理' }
      },
      {
        path: 'bookings/:id',
        name: 'BookingDetail',
        component: () => import('@/views/BookingDetail.vue'),
        meta: { title: '预订详情' }
      },
      {
        path: 'calendar',
        name: 'Calendar',
        component: () => import('@/views/Calendar.vue'),
        meta: { title: '房态日历' }
      },
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('@/views/Stats.vue'),
        meta: { title: '营收统计' }
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import('@/views/Reviews.vue'),
        meta: { title: '评价管理' }
      },
      {
        path: 'holidays',
        name: 'Holidays',
        component: () => import('@/views/Holidays.vue'),
        meta: { title: '节假日管理', roles: ['admin'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  
  if (to.meta.requiresAuth && !auth.token) {
    next('/login')
  } else if (to.meta.guest && auth.token) {
    if (to.path === '/login') {
      if (auth.isAdmin) {
        next('/dashboard')
      } else {
        next('/calendar')
      }
    } else {
      next('/')
    }
  } else if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    if (auth.isAdmin) {
      next('/dashboard')
    } else {
      next('/calendar')
    }
  } else if (to.path === '/' || to.path === '') {
    if (auth.isAdmin) {
      next('/dashboard')
    } else {
      next('/calendar')
    }
  } else {
    next()
  }
})

export default router
