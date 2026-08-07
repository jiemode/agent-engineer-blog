import http from './http'

const TOKEN_KEY = 'access_token'

interface LoginResponse {
  access_token: string
  token_type: string
}

export async function login(username: string, password: string): Promise<void> {
  const { data } = await http.post<LoginResponse>('/auth/login', {
    username,
    password,
  })
  localStorage.setItem(TOKEN_KEY, data.access_token)
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}
