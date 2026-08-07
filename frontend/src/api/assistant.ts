import { getToken } from './auth'
import http, { apiBaseUrl } from './http'

export interface AssistantSource {
  title: string
  snippet: string
}

export interface AssistantResponse {
  answer: string
  sources: AssistantSource[]
}

export async function askAssistant(message: string): Promise<AssistantResponse> {
  const token = getToken()
  const { data } = await http.post<AssistantResponse>(
    '/assistant/chat',
    { message, history: [] },
    token ? { headers: { Authorization: `Bearer ${token}` } } : {},
  )
  return data
}

export async function askAssistantStream(
  message: string,
  history: { role: string; content: string }[],
  onDelta: (text: string) => void,
  onSources: (sources: AssistantSource[]) => void,
): Promise<string> {
  const token = getToken()
  const response = await fetch(`${apiBaseUrl}/api/assistant/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, history }),
  })
  if (!response.ok || !response.body) throw new Error('stream failed')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let answer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.trim()) continue
      const event = JSON.parse(line)
      if (event.type === 'sources') onSources(event.sources)
      if (event.type === 'delta') {
        answer += event.content
        onDelta(answer)
      }
      if (event.type === 'done') return event.answer
      if (event.type === 'error') throw new Error(event.detail)
    }
  }
  return answer
}
