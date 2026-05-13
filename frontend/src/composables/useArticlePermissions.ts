import { computed, type ComputedRef } from 'vue'
import { useAdminStore } from '@/stores/admin'

interface ArticleLike {
  author?: { id: string } | null
}

interface ArticlePermissionsResult {
  canEdit: ComputedRef<boolean>
  canDelete: ComputedRef<boolean>
  canPublish: ComputedRef<boolean>
}

const PERMISSIONS: Record<string, Set<string>> = {
  admin: new Set(['create', 'edit_own', 'edit_others', 'delete', 'publish', 'reassign']),
  editor: new Set(['create', 'edit_own', 'edit_others', 'delete', 'publish']),
  contributor: new Set(['create', 'edit_own', 'delete']),
}

export function useArticlePermissions(article: ArticleLike | null): ArticlePermissionsResult {
  const store = useAdminStore()

  const canEdit = computed(() => {
    const user = store.user
    if (!user) return false

    const allowed = PERMISSIONS[user.role] ?? new Set()
    const isOwn = article?.author?.id === user.id

    if (isOwn) return allowed.has('edit_own')
    return allowed.has('edit_others')
  })

  const canDelete = computed(() => {
    const user = store.user
    if (!user) return false
    const allowed = PERMISSIONS[user.role] ?? new Set()
    if (!allowed.has('delete')) return false
    if (user.role === 'contributor') {
      return article?.author?.id === user.id
    }
    return true
  })

  const canPublish = computed(() => {
    const user = store.user
    if (!user) return false
    return (PERMISSIONS[user.role] ?? new Set()).has('publish')
  })

  return { canEdit, canDelete, canPublish }
}
