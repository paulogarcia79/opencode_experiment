import { ref, watch, onUnmounted, getCurrentInstance, type Ref } from 'vue'
import { getAuthHeaders } from '@/composables/useAdminApi'

export interface AutoSaveForm {
  title: string
  description: string
  content: Record<string, unknown>
  tag_names: string[]
}

export type AutoSaveStatus = 'idle' | 'saving' | 'saved' | 'retrying' | 'error'

export interface UseAutoSaveOptions {
  onCreated?: (id: string) => void
}

export function useAutoSave(
  form: Ref<AutoSaveForm>,
  articleId: Ref<string | null>,
  options: UseAutoSaveOptions = {}
) {
  const status = ref<AutoSaveStatus>('idle')
  const error = ref<string | null>(null)
  const lastSavedAt = ref<Date | null>(null)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null
  let deferralTimer: ReturnType<typeof setTimeout> | null = null
  let heartbeatTimer: ReturnType<typeof setTimeout> | null = null
  let retryTimer: ReturnType<typeof setTimeout> | null = null
  let lastSavedPayload: string | null = null
  let firstContentWithoutTitleAt: number | null = null
  let isSaving = false
  let retryCount = 0

  function isEmptyForm(f: AutoSaveForm): boolean {
    const hasTitle = f.title.trim().length > 0
    const hasDescription = f.description.trim().length > 0
    const hasTags = f.tag_names.length > 0
    const hasContent =
      f.content.content &&
      Array.isArray(f.content.content) &&
      f.content.content.length > 0 &&
      !(f.content.content.length === 1 &&
        (f.content.content[0] as Record<string, unknown>).type === 'paragraph' &&
        !((f.content.content[0] as Record<string, unknown>).content as Array<unknown>)?.length)

    return !hasTitle && !hasDescription && !hasTags && !hasContent
  }

  function scheduleHeartbeat() {
    if (heartbeatTimer) clearTimeout(heartbeatTimer)
    heartbeatTimer = setTimeout(() => {
      const payload = {
        title: form.value.title,
        description: form.value.description || undefined,
        content: form.value.content,
        tag_names: form.value.tag_names,
      }
      const payloadJson = JSON.stringify(payload)
      // Only heartbeat if dirty and not currently saving
      if (!isSaving && lastSavedPayload !== payloadJson && !isEmptyForm(form.value)) {
        doSave()
      }
      scheduleHeartbeat()
    }, 30000)
  }

  async function doSave() {
    const payload = {
      title: form.value.title,
      description: form.value.description || undefined,
      content: form.value.content,
      tag_names: form.value.tag_names,
    }
    const payloadJson = JSON.stringify(payload)

    // Skip if unchanged since last save
    if (lastSavedPayload === payloadJson) return

    // Skip if effectively empty
    if (isEmptyForm(form.value)) return

    // For new articles without a title, defer creation until title is added
    // or 60 seconds of content editing have elapsed
    if (!articleId.value && !form.value.title.trim()) {
      const now = Date.now()
      if (firstContentWithoutTitleAt === null) {
        firstContentWithoutTitleAt = now
        // Schedule a retry when the deferral period expires
        const elapsed = 0
        const remaining = 60000 - elapsed
        if (deferralTimer) clearTimeout(deferralTimer)
        deferralTimer = setTimeout(() => {
          doSave()
        }, remaining)
        return
      }
      if (now - firstContentWithoutTitleAt < 60000) {
        return
      }
    } else {
      firstContentWithoutTitleAt = null
      if (deferralTimer) {
        clearTimeout(deferralTimer)
        deferralTimer = null
      }
    }

    if (isSaving) return
    isSaving = true
    status.value = 'saving'
    error.value = null

    try {
      let res: Response

      if (articleId.value) {
        // Update existing article
        res = await fetch(`/api/admin/articles/${articleId.value}/autosave`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          body: payloadJson,
        })
      } else {
        // Create new article
        res = await fetch('/api/admin/articles/autosave', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
          body: payloadJson,
        })
      }

      if (!res.ok) {
        throw new Error('Auto-save failed')
      }

      const data = await res.json()

      // If we just created a new article, update the articleId and notify
      if (!articleId.value && data.id) {
        articleId.value = data.id
        options.onCreated?.(data.id)
      }

      lastSavedPayload = payloadJson
      lastSavedAt.value = new Date()
      status.value = 'saved'
      retryCount = 0
      if (retryTimer) {
        clearTimeout(retryTimer)
        retryTimer = null
      }
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Auto-save failed'
      error.value = message
      if (retryCount < 3) {
        retryCount++
        const backoff = Math.pow(2, retryCount - 1) * 1000 // 1s, 2s, 4s
        status.value = 'retrying'
        if (retryTimer) clearTimeout(retryTimer)
        retryTimer = setTimeout(() => {
          doSave()
        }, backoff)
      } else {
        status.value = 'error'
      }
    } finally {
      isSaving = false
    }
  }

  watch(
    () => ({ ...form.value }),
    () => {
      // Reset retry count on new user input
      retryCount = 0
      if (retryTimer) {
        clearTimeout(retryTimer)
        retryTimer = null
      }
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => {
        doSave()
      }, 2000)
    },
    { deep: true }
  )

  // Start heartbeat
  scheduleHeartbeat()

  if (getCurrentInstance()) {
    onUnmounted(() => {
      if (debounceTimer) clearTimeout(debounceTimer)
      if (deferralTimer) clearTimeout(deferralTimer)
      if (heartbeatTimer) clearTimeout(heartbeatTimer)
      if (retryTimer) clearTimeout(retryTimer)
    })
  }

  function retry() {
    doSave()
  }

  return {
    status,
    error,
    lastSavedAt,
    retry,
  }
}
