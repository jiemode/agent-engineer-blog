import { getToken } from './auth'
import http from './http'

export interface Post {
  id: number
  title: string
  content: string
  tags: string
  created_at: string
}

export interface PostInput {
  title: string
  content: string
  tags: string[]
}

function authHeaders() {
  const token = getToken()
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {}
}

export async function fetchPosts(): Promise<Post[]> {
  const { data } = await http.get<Post[]>('/posts')
  return data
}

export async function fetchPost(id: number | string): Promise<Post> {
  const { data } = await http.get<Post>(`/posts/${id}`)
  return data
}

export async function createPost(input: PostInput): Promise<Post> {
  const { data } = await http.post<Post>('/posts', input, authHeaders())
  return data
}

export async function deletePost(id: number): Promise<void> {
  await http.delete(`/posts/${id}`, authHeaders())
}
