<template>
  <div class="app-layout">
    <!-- 侧边菜单 -->
    <div class="sidebar" :class="{ 'sidebar-collapse': isCollapse }">
      <div class="logo-container">
        <img src="@/assets/logo.png" alt="Logo" class="logo">
        <span v-if="!isCollapse" class="title">ArtiOps</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="isCollapse"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <template v-for="(route, index) in routes" :key="index">
          <!-- 有子菜单 -->
          <el-sub-menu v-if="route.children && route.children.length > 0 && !route.hiddenInMenu" :index="route.path">
            <template #title>
              <el-icon>
                <component :is="route.meta?.icon || 'Document'" />
              </el-icon>
              <span>{{ route.meta?.title }}</span>
            </template>
            <el-menu-item 
              v-for="(child, childIndex) in route.children.filter(item => !item.meta?.hiddenInMenu)" 
              :key="childIndex" 
              :index="route.path + '/' + child.path"
            >
              <el-icon>
                <component :is="child.meta?.icon || 'Document'" />
              </el-icon>
              <span>{{ child.meta?.title }}</span>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 无子菜单 -->
          <el-menu-item v-else-if="!route.hiddenInMenu" :index="route.path">
            <el-icon>
              <component :is="route.meta?.icon || 'Document'" />
            </el-icon>
            <span>{{ route.meta?.title }}</span>
          </el-menu-item>
        </template>
      </el-menu>
    </div>
    
    <!-- 内容区域 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <div class="header">
        <div class="left">
          <el-icon class="collapse-btn" @click="toggleSidebar">
            <component :is="isCollapse ? 'Expand' : 'Fold'" />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta?.title">{{ currentRoute.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="right">
          <el-dropdown trigger="click">
            <span class="user-dropdown">
              {{ userInfo.realName || userInfo.username }}
              <el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="showUserInfo">个人信息</el-dropdown-item>
                <el-dropdown-item @click="showChangePassword">修改密码</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 主要内容 -->
      <div class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Expand, Fold } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 当前路由信息
const currentRoute = computed(() => route)

// 侧边栏折叠状态
const isCollapse = ref(false)

// 获取路由菜单
const routes = computed(() => {
  return router.options.routes.filter(route => {
    return route.path !== '/login' && route.path !== '/:pathMatch(.*)*'
  })
})

// 当前激活的菜单
const activeMenu = computed(() => {
  const { meta, path } = route
  if (meta?.activeMenu) {
    return meta.activeMenu
  }
  return path
})

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 显示用户信息
const showUserInfo = () => {
  ElMessage.info('功能开发中')
}

// 显示修改密码弹窗
const showChangePassword = () => {
  ElMessage.info('功能开发中')
}

// 退出登录
const logout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {})
}
</script>

<style lang="scss" scoped>
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  
  .sidebar {
    width: 210px;
    height: 100%;
    background-color: #304156;
    transition: width 0.3s;
    overflow-y: auto;
    overflow-x: hidden;
    
    &.sidebar-collapse {
      width: 64px;
    }
    
    .logo-container {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0 10px;
      background-color: #2b3649;
      
      .logo {
        width: 32px;
        height: 32px;
      }
      
      .title {
        margin-left: 10px;
        color: #fff;
        font-weight: bold;
        font-size: 18px;
        white-space: nowrap;
      }
    }
    
    .sidebar-menu {
      border-right: none;
      
      :deep(.el-menu-item), :deep(.el-sub-menu__title) {
        height: 50px;
        line-height: 50px;
      }
    }
  }
  
  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    
    .header {
      height: 60px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 15px;
      border-bottom: 1px solid #eee;
      background-color: #fff;
      
      .left {
        display: flex;
        align-items: center;
        
        .collapse-btn {
          padding: 8px;
          font-size: 20px;
          cursor: pointer;
          margin-right: 15px;
          
          &:hover {
            color: #409EFF;
          }
        }
      }
      
      .right {
        .user-dropdown {
          cursor: pointer;
          color: #333;
          
          &:hover {
            color: #409EFF;
          }
        }
      }
    }
    
    .content {
      flex: 1;
      padding: 15px;
      overflow-y: auto;
      background-color: #f5f7fa;
    }
  }
}
</style> 