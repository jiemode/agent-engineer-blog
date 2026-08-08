import { describe, expect, it } from 'vitest'
import type { Post } from '../api/posts'
import {
  buildCategories,
  computeStats,
  filterPosts,
  getLatestPosts,
  getRelatedPosts,
  splitTags,
} from './posts'

const samplePosts: Post[] = [
  {
    id: 1,
    title: 'FastAPI Router',
    content: '# heading\n- item\n```python\nx=1\n```',
    tags: 'fastapi, architecture',
    created_at: '2026-08-01',
  },
  {
    id: 2,
    title: 'Pydantic Models',
    content: 'plain text',
    tags: 'python, fastapi',
    created_at: '2026-08-02',
  },
  {
    id: 3,
    title: 'Git Staging',
    content: 'note',
    tags: 'git',
    created_at: '2026-08-03',
  },
]

describe('post utilities', () => {
  it('splits comma separated tags', () => {
    expect(splitTags(' fastapi , architecture ')).toEqual([
      'fastapi',
      'architecture',
    ])
  })

  it('builds categories with counts', () => {
    const categories = buildCategories(samplePosts)
    expect(categories.find((c) => c.name === 'fastapi')?.count).toBe(2)
    expect(categories).toHaveLength(4)
  })

  it('filters by category and search text', () => {
    expect(filterPosts(samplePosts, { category: 'fastapi' })).toHaveLength(2)
    expect(filterPosts(samplePosts, { search: 'router' })).toHaveLength(1)
  })

  it('returns newest posts first', () => {
    expect(getLatestPosts(samplePosts, 2).map((p) => p.id)).toEqual([3, 2])
  })

  it('computes stats from real content', () => {
    const stats = computeStats(samplePosts)
    expect(stats.posts).toBe(3)
    expect(stats.categories).toBe(4)
    expect(stats.knowledgeBlocks).toBe(4)
    expect(stats.totalChars).toBeGreaterThan(0)
  })

  it('ranks related posts by shared tags', () => {
    expect(getRelatedPosts(samplePosts, samplePosts[0]).map((p) => p.id)).toEqual([
      2,
      3,
    ])
  })
})
