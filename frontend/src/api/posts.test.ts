import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('./http', () => ({ default: { get: vi.fn() } }))

import http from './http'
import { fetchPost } from './posts'

const mockedGet = vi.mocked(http.get)

describe('fetchPost', () => {
  beforeEach(() => {
    mockedGet.mockReset()
  })

  it('requests one post by id', async () => {
    mockedGet.mockResolvedValue({
      data: {
        id: 7,
        title: 'Title',
        content: 'Body',
        tags: 'fastapi',
        created_at: '2026-08-08',
      },
    })

    const post = await fetchPost(7)

    expect(mockedGet).toHaveBeenCalledWith('/posts/7')
    expect(post.title).toBe('Title')
  })
})
