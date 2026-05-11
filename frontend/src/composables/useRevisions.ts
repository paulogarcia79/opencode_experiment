import { ref, type Ref } from 'vue'
import { fetchRevisions, fetchRevision, restoreRevision, type RevisionListItem, type Revision } from '@/composables/useAdminApi'

export function useRevisions(articleId: Ref<string>) {
  const revisions = ref<RevisionListItem[]>([])
  const currentRevision = ref<Revision | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchList() {
    if (!articleId.value) return
    loading.value = true
    error.value = null
    try {
      revisions.value = await fetchRevisions(articleId.value)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch revisions'
    } finally {
      loading.value = false
    }
  }

  async function fetch(versionNumber: number) {
    if (!articleId.value) return
    loading.value = true
    error.value = null
    try {
      currentRevision.value = await fetchRevision(articleId.value, versionNumber)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch revision'
    } finally {
      loading.value = false
    }
  }

  async function restore(versionNumber: number) {
    if (!articleId.value) return
    loading.value = true
    error.value = null
    try {
      const result = await restoreRevision(articleId.value, versionNumber)
      await fetchList()
      return result
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to restore revision'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    revisions,
    currentRevision,
    loading,
    error,
    fetchList,
    fetch,
    restore,
  }
}
