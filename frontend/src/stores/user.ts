import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login, logout, getUserInfo } from '@/api/user'
import { ElMessage } from 'element-plus'

// 用户信息接口
export interface UserInfo {
  id: number
  username: string
  realName: string
  role: number
  roleName: string
  [key: string]: any
}

export const useUserStore = defineStore('user', () => {
  // 用户token
  const token = ref<string>(localStorage.getItem('token') || '')
  
  // 用户信息
  const userInfo = ref<UserInfo>({
    id: 0,
    username: '',
    realName: '',
    role: 0,
    roleName: ''
  })
  
  // 设置token
  const setToken = (value: string) => {
    token.value = value
    localStorage.setItem('token', value)
  }
  
  // 清除token
  const clearToken = () => {
    token.value = ''
    localStorage.removeItem('token')
  }
  
  // 用户登录
  const userLogin = async (loginForm: { username: string; password: string }) => {
    try {
      const response = await login(loginForm)
      const { access, refresh, ...user } = response.data
      
      // 保存token
      setToken(access)
      localStorage.setItem('refresh_token', refresh)
      
      // 保存用户信息
      userInfo.value = user
      
      return true
    } catch (error) {
      ElMessage.error('登录失败，请检查用户名和密码')
      return false
    }
  }
  
  // 退出登录
  const userLogout = async () => {
    try {
      if (token.value) {
        await logout()
      }
    } catch (error) {
      console.error('登出错误', error)
    } finally {
      clearToken()
      userInfo.value = {
        id: 0,
        username: '',
        realName: '',
        role: 0,
        roleName: ''
      }
      localStorage.removeItem('refresh_token')
    }
  }
  
  // 获取用户信息
  const fetchUserInfo = async () => {
    try {
      if (!token.value) return false
      
      const response = await getUserInfo()
      userInfo.value = response.data
      return true
    } catch (error) {
      clearToken()
      return false
    }
  }
  
  return {
    token,
    userInfo,
    login: userLogin,
    logout: userLogout,
    fetchUserInfo
  }
}) 