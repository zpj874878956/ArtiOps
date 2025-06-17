import request from '@/utils/request'

/**
 * 用户登录
 */
export function login(data: { username: string; password: string }) {
  return request({
    url: '/api/v1/users/login/',
    method: 'post',
    data
  })
}

/**
 * 用户登出
 */
export function logout() {
  return request({
    url: '/api/v1/users/logout/',
    method: 'post'
  })
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
  return request({
    url: '/api/v1/users/profile/',
    method: 'get'
  })
}

/**
 * 修改密码
 */
export function changePassword(data: { old_password: string; new_password: string; confirm_password: string }) {
  return request({
    url: '/api/v1/users/update_password/',
    method: 'post',
    data
  })
}

/**
 * 获取用户列表
 */
export function getUserList(params: any) {
  return request({
    url: '/api/v1/users/',
    method: 'get',
    params
  })
}

/**
 * 创建用户
 */
export function createUser(data: any) {
  return request({
    url: '/api/v1/users/',
    method: 'post',
    data
  })
}

/**
 * 更新用户
 */
export function updateUser(id: number, data: any) {
  return request({
    url: `/api/v1/users/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 */
export function deleteUser(id: number) {
  return request({
    url: `/api/v1/users/${id}/`,
    method: 'delete'
  })
}

/**
 * 重置用户密码
 */
export function resetUserPassword(id: number) {
  return request({
    url: `/api/v1/users/${id}/reset_password/`,
    method: 'post'
  })
}

/**
 * 切换用户状态
 */
export function toggleUserStatus(id: number) {
  return request({
    url: `/api/v1/users/${id}/toggle_status/`,
    method: 'post'
  })
} 