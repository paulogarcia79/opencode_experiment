import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'
import { useArticlePermissions } from '@/composables/useArticlePermissions'

function makeArticle(authorId: string | null = null) {
  return {
    id: 'article-1',
    title: 'Test Article',
    slug: 'test-article',
    content: { type: 'doc' },
    description: null,
    status: 'draft',
    send_newsletter: true,
    published_at: null,
    scheduled_for: null,
    search_text: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    author: authorId ? { id: authorId, email: 'author@example.com' } : null,
    tags: [],
  }
}

describe('useArticlePermissions', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('admin', () => {
    beforeEach(() => {
      const store = useAdminStore()
      store.setUser({
        id: 'admin-1',
        email: 'admin@example.com',
        role: 'admin',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
      })
    })

    it('can edit own article', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('admin-1'))
      expect(canEdit.value).toBe(true)
      expect(canDelete.value).toBe(true)
      expect(canPublish.value).toBe(true)
    })

    it('can edit others article', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('other-1'))
      expect(canEdit.value).toBe(true)
      expect(canDelete.value).toBe(true)
      expect(canPublish.value).toBe(true)
    })

    it('can edit article with no author', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle(null))
      expect(canEdit.value).toBe(true)
      expect(canDelete.value).toBe(true)
      expect(canPublish.value).toBe(true)
    })
  })

  describe('editor', () => {
    beforeEach(() => {
      const store = useAdminStore()
      store.setUser({
        id: 'editor-1',
        email: 'editor@example.com',
        role: 'editor',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
      })
    })

    it('can edit own article', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('editor-1'))
      expect(canEdit.value).toBe(true)
      expect(canDelete.value).toBe(true)
      expect(canPublish.value).toBe(true)
    })

    it('can edit others article', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('contributor-1'))
      expect(canEdit.value).toBe(true)
      expect(canDelete.value).toBe(true)
      expect(canPublish.value).toBe(true)
    })
  })

  describe('contributor', () => {
    beforeEach(() => {
      const store = useAdminStore()
      store.setUser({
        id: 'contributor-1',
        email: 'contributor@example.com',
        role: 'contributor',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
      })
    })

    it('can edit own article', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('contributor-1'))
      expect(canEdit.value).toBe(true)
      expect(canDelete.value).toBe(true)
      expect(canPublish.value).toBe(false)
    })

    it('cannot edit others article', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('other-1'))
      expect(canEdit.value).toBe(false)
      expect(canDelete.value).toBe(false)
      expect(canPublish.value).toBe(false)
    })

    it('cannot edit article with no author', () => {
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle(null))
      expect(canEdit.value).toBe(false)
      expect(canDelete.value).toBe(false)
      expect(canPublish.value).toBe(false)
    })
  })

  describe('unknown role', () => {
    beforeEach(() => {
      const store = useAdminStore()
      store.setUser({
        id: 'user-1',
        email: 'user@example.com',
        role: 'contributor',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
      })
    })

    it('defaults to no permissions when user is null', () => {
      const store = useAdminStore()
      store.clearUser()
      const { canEdit, canDelete, canPublish } = useArticlePermissions(makeArticle('user-1'))
      expect(canEdit.value).toBe(false)
      expect(canDelete.value).toBe(false)
      expect(canPublish.value).toBe(false)
    })
  })
})
