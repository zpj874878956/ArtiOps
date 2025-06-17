import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

// 布局组件
const Layout = () => import('@/layout/index.vue')

// 路由配置
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', hiddenInMenu: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '控制台', icon: 'el-icon-menu' }
      }
    ]
  },
  {
    path: '/project',
    component: Layout,
    meta: { title: '项目管理', icon: 'el-icon-folder' },
    children: [
      {
        path: 'list',
        name: 'ProjectList',
        component: () => import('@/views/project/list.vue'),
        meta: { title: '项目列表' }
      },
      {
        path: 'detail/:id',
        name: 'ProjectDetail',
        component: () => import('@/views/project/detail.vue'),
        meta: { title: '项目详情', hiddenInMenu: true }
      }
    ]
  },
  {
    path: '/build',
    component: Layout,
    meta: { title: '构建管理', icon: 'el-icon-menu' },
    children: [
      {
        path: 'task',
        name: 'BuildTask',
        component: () => import('@/views/build/task.vue'),
        meta: { title: '构建任务' }
      },
      {
        path: 'history',
        name: 'BuildHistory',
        component: () => import('@/views/build/history.vue'),
        meta: { title: '构建历史' }
      }
    ]
  },
  {
    path: '/credential',
    component: Layout,
    meta: { title: '凭据管理', icon: 'el-icon-key' },
    children: [
      {
        path: 'list',
        name: 'CredentialList',
        component: () => import('@/views/credential/list.vue'),
        meta: { title: '凭据列表' }
      }
    ]
  },
  {
    path: '/environment',
    component: Layout,
    meta: { title: '环境管理', icon: 'el-icon-setting' },
    children: [
      {
        path: 'list',
        name: 'EnvironmentList',
        component: () => import('@/views/environment/list.vue'),
        meta: { title: '环境列表' }
      }
    ]
  },
  {
    path: '/system',
    component: Layout,
    meta: { title: '系统管理', icon: 'el-icon-setting' },
    children: [
      {
        path: 'user',
        name: 'UserManagement',
        component: () => import('@/views/system/user.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'role',
        name: 'RoleManagement',
        component: () => import('@/views/system/role.vue'),
        meta: { title: '角色管理' }
      },
      {
        path: 'config',
        name: 'SystemConfig',
        component: () => import('@/views/system/config.vue'),
        meta: { title: '系统配置' }
      },
      {
        path: 'log',
        name: 'SystemLog',
        component: () => import('@/views/system/log.vue'),
        meta: { title: '系统日志' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/error/404.vue'),
    meta: { title: '404', hiddenInMenu: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 导航守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `${to.meta.title} - ArtiOps运维平台`
  
  // 判断是否需要登录
  const token = localStorage.getItem('token')
  if (to.path !== '/login' && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router 