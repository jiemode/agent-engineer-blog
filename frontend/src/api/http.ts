import axios from 'axios'

// 开发环境 VITE_API_BASE_URL 为空 -> 走 Vite 代理 /api；
// 部署到 GitHub Pages 时，通过它指向真实后端地址。
export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || ''

const http = axios.create({
  baseURL: `${apiBaseUrl}/api`,
})

export default http
