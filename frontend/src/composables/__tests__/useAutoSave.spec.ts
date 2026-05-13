import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { createPinia, setActivePinia } from 'pinia'
import { useAdminStore } from '@/stores/admin'
import { useAutoSave } from '@/composables/useAutoSave'

describe('useAutoSave', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.stubGlobal('fetch', vi.fn())
    setActivePinia(createPinia())
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('debounces save for 2 seconds after typing', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { status, markFormTouched } = useAutoSave(form, articleId)

    expect(status.value).toBe('idle')

    // Simulate user touching the form, then typing
    markFormTouched()
    form.value.title = 'Hello World'
    await nextTick()

    // Immediately after typing, should still be idle (debouncing)
    expect(status.value).toBe('idle')

    // Advance 2 seconds and flush async microtasks
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    // Should have triggered save
    expect(mockFetch).toHaveBeenCalledTimes(1)
    expect(status.value).toBe('saved')
  })

  it('includes auth headers in the request', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { markFormTouched } = useAutoSave(form, articleId)

    markFormTouched()
    form.value.title = 'Updated'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/articles/article-1/autosave'),
      expect.objectContaining({
        method: 'PUT',
        headers: expect.objectContaining({
          Authorization: 'Bearer test-token',
          'Content-Type': 'application/json',
        }),
      })
    )
  })

  it('skips save when form is unchanged since last save', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { markFormTouched } = useAutoSave(form, articleId)

    // First change triggers save after 2s
    markFormTouched()
    form.value.title = 'Hello World'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    expect(mockFetch).toHaveBeenCalledTimes(1)

    // Same change again should NOT trigger another save
    form.value.title = 'Hello World'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it('skips save when form is effectively empty', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: '',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { markFormTouched } = useAutoSave(form, articleId)

    // Trigger a watch by mutating (even to same empty value)
    markFormTouched()
    form.value.title = ''
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('creates a new article via POST when articleId is null', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'new-article-123', slug: 'hello-world' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: '',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref<string | null>(null)
    const onCreated = vi.fn()

    const { markFormTouched } = useAutoSave(form, articleId, { onCreated })

    markFormTouched()
    form.value.title = 'Hello World'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    expect(mockFetch).toHaveBeenCalledTimes(1)
    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/articles/autosave'),
      expect.objectContaining({ method: 'POST' })
    )
    expect(onCreated).toHaveBeenCalledWith('new-article-123')
  })

  it('defers creating a new article when title is empty', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'new-article-123' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: '',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Some content' }] }] },
      tag_names: [],
    })
    const articleId = ref<string | null>(null)

    const { markFormTouched } = useAutoSave(form, articleId)

    // Type content without a title
    markFormTouched()
    form.value.content = { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'More content' }] }] }
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    // Should NOT have created article yet (no title)
    expect(mockFetch).not.toHaveBeenCalled()

    // After 60 seconds, should create even without title
    await vi.advanceTimersByTimeAsync(60000)
    await nextTick()

    expect(mockFetch).toHaveBeenCalledTimes(1)
  })

  it('force-saves every 30 seconds via heartbeat when continuously typing', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { markFormTouched } = useAutoSave(form, articleId)

    // Type continuously every second for 35 seconds
    for (let i = 0; i < 35; i++) {
      markFormTouched()
      form.value.title = `Hello ${i}`
      await nextTick()
      await vi.advanceTimersByTimeAsync(1000)
    }

    // Should have exactly 1 heartbeat save at the 30s mark
    expect(mockFetch.mock.calls.length).toBe(1)
  })

  it('retries failed saves with exponential backoff up to 3 times', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { status, retry, markFormTouched } = useAutoSave(form, articleId)

    // Trigger a save
    markFormTouched()
    form.value.title = 'Hello World'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    // First attempt failed, status should show retrying
    expect(mockFetch).toHaveBeenCalledTimes(1)
    expect(status.value).toBe('retrying')

    // Retry 1 after 1 second
    await vi.advanceTimersByTimeAsync(1000)
    await nextTick()
    expect(mockFetch).toHaveBeenCalledTimes(2)
    expect(status.value).toBe('retrying')

    // Retry 2 after 2 seconds
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()
    expect(mockFetch).toHaveBeenCalledTimes(3)
    expect(status.value).toBe('retrying')

    // Retry 3 after 4 seconds
    await vi.advanceTimersByTimeAsync(4000)
    await nextTick()
    expect(mockFetch).toHaveBeenCalledTimes(4)

    // After 3 retries, should be in persistent error state
    expect(status.value).toBe('error')

    // Manual retry should trigger another attempt
    retry()
    await nextTick()
    await vi.advanceTimersByTimeAsync(0)
    await nextTick()
    expect(mockFetch).toHaveBeenCalledTimes(5)
  })

  it('does not auto-save when form changes but formTouched is false', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    useAutoSave(form, articleId)

    // Change form without calling markFormTouched first
    form.value.title = 'Hello World'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    // Should NOT have called fetch (formTouched is false)
    expect(mockFetch).not.toHaveBeenCalled()
  })

  it('auto-saves when form changes after calling markFormTouched', async () => {
    const store = useAdminStore()
    store.token = 'test-token'

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ id: 'article-1' }),
    })
    vi.stubGlobal('fetch', mockFetch)

    const form = ref({
      title: 'Hello',
      description: '',
      content: { type: 'doc', content: [{ type: 'paragraph' }] },
      tag_names: [],
    })
    const articleId = ref('article-1')

    const { markFormTouched } = useAutoSave(form, articleId)

    markFormTouched()
    form.value.title = 'Hello World'
    await nextTick()
    await vi.advanceTimersByTimeAsync(2000)
    await nextTick()

    expect(mockFetch).toHaveBeenCalledTimes(1)
  })
})
