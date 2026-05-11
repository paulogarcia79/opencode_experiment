import { ref } from 'vue'
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useRevisions } from '@/composables/useRevisions'
import * as useAdminApi from '@/composables/useAdminApi'

describe('useRevisions', () => {
  beforeEach(() => {
    localStorage.clear()
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  describe('fetchList', () => {
    it('fetches revision list and populates revisions ref', async () => {
      const mockRevisions = [
        { version_number: 2, change_type: 'save', title: 'V2', created_at: '2025-01-15T10:00:00' },
        { version_number: 1, change_type: 'save', title: 'V1', created_at: '2025-01-15T09:00:00' },
      ]
      vi.spyOn(useAdminApi, 'fetchRevisions').mockResolvedValue(mockRevisions)

      const { revisions, fetchList } = useRevisions(ref('article-1'))
      await fetchList()

      expect(revisions.value).toEqual(mockRevisions)
    })

    it('sets error on failure', async () => {
      vi.spyOn(useAdminApi, 'fetchRevisions').mockRejectedValue(new Error('Network error'))

      const { revisions, error, fetchList } = useRevisions(ref('article-1'))
      await fetchList()

      expect(revisions.value).toEqual([])
      expect(error.value).toBe('Network error')
    })
  })

  describe('fetch', () => {
    it('fetches single revision and populates currentRevision ref', async () => {
      const mockRevision = {
        version_number: 1,
        change_type: 'save',
        title: 'V1',
        content: { type: 'doc' },
        description: 'Desc',
        tag_names: ['tech'],
        created_at: '2025-01-15T09:00:00',
      }
      vi.spyOn(useAdminApi, 'fetchRevision').mockResolvedValue(mockRevision)

      const { currentRevision, fetch } = useRevisions(ref('article-1'))
      await fetch(1)

      expect(currentRevision.value).toEqual(mockRevision)
    })

    it('sets error on failure', async () => {
      vi.spyOn(useAdminApi, 'fetchRevision').mockRejectedValue(new Error('Not found'))

      const { currentRevision, error, fetch } = useRevisions(ref('article-1'))
      await fetch(999)

      expect(currentRevision.value).toBeNull()
      expect(error.value).toBe('Not found')
    })
  })

  describe('restore', () => {
    it('calls restore API and refreshes revision list', async () => {
      const mockArticle = { id: 'article-1', title: 'Restored' }
      const mockRevisions = [
        { version_number: 2, change_type: 'restore', title: 'Restored', created_at: '2025-01-15T11:00:00' },
      ]
      vi.spyOn(useAdminApi, 'restoreRevision').mockResolvedValue(mockArticle)
      vi.spyOn(useAdminApi, 'fetchRevisions').mockResolvedValue(mockRevisions)

      const { revisions, restore } = useRevisions(ref('article-1'))
      const result = await restore(1)

      expect(result).toEqual(mockArticle)
      expect(revisions.value).toEqual(mockRevisions)
    })

    it('sets error and rethrows on failure', async () => {
      vi.spyOn(useAdminApi, 'restoreRevision').mockRejectedValue(new Error('Restore failed'))

      const { error, restore } = useRevisions(ref('article-1'))
      await expect(restore(1)).rejects.toThrow('Restore failed')
      expect(error.value).toBe('Restore failed')
    })
  })
})
