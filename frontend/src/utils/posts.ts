import type { Post } from '../api/posts'

export interface Category {
  name: string
  count: number
}

export interface BlogStats {
  posts: number
  categories: number
  knowledgeBlocks: number
  totalChars: number
}

export function splitTags(tags: string): string[] {
  return tags
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean)
}

export function buildCategories(posts: Post[]): Category[] {
  const counts = new Map<string, number>()
  for (const post of posts) {
    for (const tag of splitTags(post.tags)) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1)
    }
  }
  return Array.from(counts.entries()).map(([name, count]) => ({ name, count }))
}

export function filterPosts(
  posts: Post[],
  filters: { search?: string; category?: string } = {},
): Post[] {
  const query = filters.search?.trim().toLowerCase() ?? ''
  const category = filters.category?.trim()
  return posts.filter((post) => {
    const matchCategory = !category || splitTags(post.tags).includes(category)
    const matchSearch =
      !query ||
      post.title.toLowerCase().includes(query) ||
      post.content.toLowerCase().includes(query)
    return matchCategory && matchSearch
  })
}

export function getLatestPosts(posts: Post[], limit: number): Post[] {
  return [...posts].sort((a, b) => b.id - a.id).slice(0, limit)
}

export function computeStats(posts: Post[]): BlogStats {
  let knowledgeBlocks = 0
  let totalChars = 0
  for (const post of posts) {
    const headings = post.content.match(/^#{1,6}\s/gm)?.length ?? 0
    const bullets = post.content.match(/^[-*+]\s/gm)?.length ?? 0
    const fences = post.content.match(/```/g)?.length ?? 0
    knowledgeBlocks += headings + bullets + fences
    totalChars += post.content.length
  }
  return {
    posts: posts.length,
    categories: buildCategories(posts).length,
    knowledgeBlocks,
    totalChars,
  }
}

function relatedScore(post: Post, tags: string[]): number {
  return splitTags(post.tags).filter((tag) => tags.includes(tag)).length
}

export function getRelatedPosts(posts: Post[], post: Post, limit = 3): Post[] {
  const tags = splitTags(post.tags)
  return posts
    .filter((item) => item.id !== post.id)
    .sort((a, b) => relatedScore(b, tags) - relatedScore(a, tags))
    .slice(0, limit)
}
