<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-display font-bold text-white">
        {{ isEditing ? 'Edit Article' : 'New Article' }}
      </h1>
      <p class="mt-1 text-sm text-slate-500">
        {{ isEditing ? 'Update your existing article' : 'Create a new blog post' }}
      </p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-8">
      <!-- Rejection Feedback Banner -->
      <div v-if="isContributor && rejectionFeedback" class="border border-accent-500/20 bg-accent-500/10 rounded-xl p-5 flex items-start gap-4">
        <div class="w-8 h-8 rounded-lg bg-accent-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
          <svg class="h-4 w-4 text-accent-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-accent-300 text-sm">Article was rejected</p>
          <p class="text-sm text-accent-400/80 mt-1">{{ rejectionFeedback }}</p>
        </div>
      </div>
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">Title</label>
        <input
          v-model="form.title"
          type="text"
          required
          :disabled="isReadOnly"
          class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          placeholder="Article title"
          @input="markFormTouched()"
        />
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">
          Description
          <span class="text-slate-600 font-normal">— optional override</span>
        </label>
        <input
          v-model="form.description"
          type="text"
          :disabled="isReadOnly"
          class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          placeholder="Brief description for the article card"
          @input="markFormTouched()"
        />
      </div>

      <!-- Tags -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">
          Tags
          <span class="text-slate-600 font-normal">— max 8</span>
        </label>
        <TagInput v-if="!isReadOnly" v-model="form.tags" />
        <div v-else class="text-sm text-slate-500 italic">Tags are not editable in read-only mode</div>
      </div>

      <!-- Content Editor -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">Content</label>
        <TipTapEditor :key="editorKey" v-model="form.content" :editable="!isReadOnly" @update:model-value="markFormTouched()" />
      </div>

      <!-- Settings -->
      <div v-if="!isReadOnly" class="flex flex-wrap items-center gap-6 p-5 rounded-xl border border-white/5 bg-white/[0.02]">
        <!-- Contributor: Read-only status badge + Submit for Review -->
        <template v-if="isContributor">
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">Status:</span>
            <span
              :class="[
                'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                form.status === 'published'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : form.status === 'pending_review'
                    ? 'bg-accent-500/10 text-accent-400 border border-accent-500/20'
                    : 'bg-slate-500/10 text-slate-400 border border-slate-500/20',
              ]"
            >
              <span
                :class="[
                  'w-1.5 h-1.5 rounded-full',
                  form.status === 'published' ? 'bg-emerald-400' : form.status === 'pending_review' ? 'bg-accent-400' : 'bg-slate-500',
                ]"
              />
              {{ form.status }}
            </span>
          </div>
          <button
            v-if="form.status === 'draft'"
            type="button"
            @click="handleSubmitForReview"
            :disabled="submitting"
            class="inline-flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer"
          >
            Submit for Review
          </button>
          <button
            v-else-if="form.status === 'pending_review'"
            type="button"
            @click="handleSubmitForReview"
            :disabled="submitting"
            class="inline-flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer"
          >
            Update Review
          </button>
          <button
            v-else-if="form.status === 'published'"
            type="button"
            @click="handleSubmitForReview"
            :disabled="submitting"
            class="inline-flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer"
          >
            Re-submit for Review
          </button>
        </template>

        <!-- Admin/Editor: Publish toggle -->
        <template v-else>
          <label v-if="canPublish" class="flex items-center gap-3 cursor-pointer">
            <div class="relative">
              <input
                v-model="form.status"
                type="checkbox"
                :true-value="'published'"
                :false-value="'draft'"
                class="peer sr-only"
              />
              <div class="w-10 h-6 rounded-full bg-white/10 peer-checked:bg-primary-600 transition-colors duration-200" />
              <div class="absolute left-1 top-1 w-4 h-4 rounded-full bg-white transition-transform duration-200 peer-checked:translate-x-4" />
            </div>
            <span class="text-sm text-slate-300">Publish immediately</span>
          </label>

          <label v-if="canPublish && form.status === 'published'" class="flex items-center gap-3 cursor-pointer">
            <div class="relative">
              <input
                v-model="form.send_newsletter"
                type="checkbox"
                class="peer sr-only"
              />
              <div class="w-10 h-6 rounded-full bg-white/10 peer-checked:bg-accent-600 transition-colors duration-200" />
              <div class="absolute left-1 top-1 w-4 h-4 rounded-full bg-white transition-transform duration-200 peer-checked:translate-x-4" />
            </div>
            <span class="text-sm text-slate-300">Send newsletter</span>
          </label>
        </template>
      </div>

      <!-- Change Author (Admin Only) -->
      <div v-if="isAdmin && isEditing" class="p-5 rounded-xl border border-white/5 bg-white/[0.02]">
        <h3 class="text-sm font-medium text-slate-400 mb-3">Change Author</h3>
        <div class="flex items-center gap-3">
          <select
            v-model="selectedAuthorId"
            class="flex-1 px-4 py-2.5 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
          >
            <option value="" disabled>Select a user</option>
            <option v-for="user in activeUsers" :key="user.id" :value="user.id">
              {{ user.email }}
            </option>
          </select>
          <button
            type="button"
            @click="handleReassign"
            :disabled="!selectedAuthorId || reassigning"
            class="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg border border-white/10 transition-all duration-200 cursor-pointer"
          >
            <svg v-if="reassigning" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span v-if="reassigning">Reassigning...</span>
            <span v-else>Reassign</span>
          </button>
        </div>
        <p v-if="reassignError" class="mt-2 text-xs text-red-400">{{ reassignError }}</p>
      </div>

      <!-- Actions -->
      <div v-if="!isReadOnly" class="flex items-center gap-3">
        <button
          v-if="!(isContributor && isEditing)"
          type="submit"
          :disabled="submitting"
          class="inline-flex items-center gap-2 px-6 py-2.5 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
        >
          <svg v-if="submitting" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span v-if="submitting">{{ isEditing ? 'Updating...' : 'Creating...' }}</span>
          <span v-else>{{ isEditing ? 'Update Article' : 'Create Article' }}</span>
        </button>
        <button
          v-if="isEditing && !isContributor"
          type="button"
          @click="handleSendPreview"
          :disabled="previewing"
          class="inline-flex items-center gap-2 px-6 py-2.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg border border-white/10 transition-all duration-200 cursor-pointer"
        >
          <svg v-if="previewing" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span v-if="previewing">Sending...</span>
          <span v-else>Send Preview</span>
        </button>
        <button
          v-if="isEditing"
          type="button"
          @click="showHistory = true"
          class="inline-flex items-center gap-2 px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium rounded-lg border border-white/10 transition-all duration-200 cursor-pointer"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          History
        </button>
        <RouterLink
          to="/admin"
          class="px-6 py-2.5 border border-white/10 text-sm font-medium text-slate-400 rounded-lg hover:bg-white/5 hover:text-white transition-all duration-200 cursor-pointer"
        >
          Cancel
        </RouterLink>

        <!-- Auto-save status -->
        <template v-if="!isReadOnly">
        <span
          v-if="autosaveStatus === 'saving'"
          class="text-xs text-slate-500 animate-pulse"
        >
          Saving...
        </span>
        <span
          v-else-if="autosaveStatus === 'saved'"
          class="text-xs text-emerald-500/80"
        >
          Saved
        </span>
        <span
          v-else-if="autosaveStatus === 'retrying'"
          class="text-xs text-amber-500/80"
        >
          Auto-save failed (retrying...)
        </span>
        <span
          v-else-if="autosaveStatus === 'error'"
          class="text-xs text-red-400 flex items-center gap-2"
        >
          Auto-save failed
          <button
            type="button"
            @click="retryAutoSave"
            class="text-xs text-primary-400 hover:text-primary-300 underline cursor-pointer"
          >
            Retry
          </button>
        </span>
        <span
          v-else-if="!isEditing && !form.title"
          class="text-xs text-slate-600"
        >
          Add a title to enable auto-save
        </span>
        </template>
      </div>

      <!-- Status Messages -->
      <div v-if="state === 'success'" class="flex items-start gap-4 p-5 rounded-xl border border-emerald-500/20 bg-emerald-500/10">
        <div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center flex-shrink-0">
          <svg class="h-5 w-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-emerald-300">Success</p>
          <p class="text-sm text-emerald-400/80 mt-0.5">{{ message }}</p>
        </div>
      </div>

      <div v-if="state === 'error'" class="flex items-start gap-4 p-5 rounded-xl border border-red-500/20 bg-red-500/10">
        <div class="w-8 h-8 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-red-300">Error</p>
          <p class="text-sm text-red-400/80 mt-0.5">{{ message }}</p>
        </div>
      </div>
    </form>

    <RevisionPanel
      :is-open="showHistory"
      :article-id="articleId || ''"
      :current-article="currentArticleForHistory"
      @close="showHistory = false"
      @restored="handleRestored"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TipTapEditor from '@/components/TipTapEditor.vue'
import TagInput from '@/components/TagInput.vue'
import RevisionPanel from '@/components/RevisionPanel.vue'
import { createArticle, updateArticle, fetchAdminArticle, sendPreviewEmail, fetchUsers, reassignArticle } from '@/composables/useAdminApi'
import { useAutoSave } from '@/composables/useAutoSave'
import { useConfirm } from '@/composables/useConfirm'
import { useAdminStore } from '@/stores/admin'
import type { TagItem } from '@/components/TagInput.vue'
import type { TipTapContent, User } from '@/types'

const route = useRoute()
const router = useRouter()
const store = useAdminStore()
const { confirm } = useConfirm()
const isEditing = ref(false)
const loadedArticle = ref<{ author?: { id: string } | null } | null>(null)

const form = ref({
  title: '',
  description: '',
  content: { type: 'doc', content: [{ type: 'paragraph' }] } as TipTapContent,
  status: 'draft',
  send_newsletter: true,
  tags: [] as TagItem[],
})

const state = ref<'idle' | 'success' | 'error'>('idle')
const message = ref('')
const submitting = ref(false)
const previewing = ref(false)
const editorKey = ref(0)
const articleId = ref<string | null>(null)
const showHistory = ref(false)

const activeUsers = ref<User[]>([])
const selectedAuthorId = ref('')
const reassigning = ref(false)
const reassignError = ref('')

const isAdmin = computed(() => store.user?.role === 'admin')
const canPublish = computed(() => {
  const user = store.user
  if (!user) return false
  return user.role === 'admin' || user.role === 'editor'
})

const isContributor = computed(() => store.user?.role === 'contributor')

const isReadOnly = computed(() => {
  if (!store.user || !loadedArticle.value) return false
  return loadedArticle.value.author?.id !== store.user.id
})

const namespace = computed(() => {
  const role = store.user?.role
  if (role === 'editor') return '/editor'
  if (role === 'contributor') return '/contributor'
  return '/admin'
})

const rejectionFeedback = ref<string | null>(null)

const currentArticleForHistory = computed(() => ({
  title: form.value.title,
  description: form.value.description,
  content: form.value.content,
  tags: form.value.tags,
}))

const autosaveForm = computed(() => ({
  title: form.value.title,
  description: form.value.description,
  content: form.value.content,
  tag_names: form.value.tags.map((t) => t.name),
}))

const { status: autosaveStatus, retry: retryAutoSave, markFormTouched } = useAutoSave(autosaveForm, articleId, {
  onCreated: (id: string) => {
    router.replace(`${namespace.value}/articles/${id}/edit`)
    isEditing.value = true
  },
})

onMounted(async () => {
  if (isAdmin.value) {
    try {
      activeUsers.value = await fetchUsers()
    } catch {
      console.error('Failed to fetch users for reassign dropdown')
    }
  }

  const id = route.params.id as string
  if (id && id !== 'new') {
    isEditing.value = true
    try {
      const article = await fetchAdminArticle(id)
      loadedArticle.value = article

      if (isContributor.value && article.author?.id !== store.user?.id) {
        router.replace(`${namespace.value}`)
        return
      }

      // Load rejection feedback for rejected articles
      if (isContributor.value) {
        rejectionFeedback.value = article.latest_rejection_feedback || null
      }

      form.value.title = article.title
      form.value.description = article.description || ''
      form.value.content = article.content || { type: 'doc', content: [{ type: 'paragraph' }] }
      form.value.status = article.status
      form.value.send_newsletter = article.send_newsletter
      form.value.tags = article.tags || []
      articleId.value = id
      editorKey.value++
    } catch (e: unknown) {
      state.value = 'error'
      message.value = 'Failed to load article: ' + (e instanceof Error ? e.message : 'Unknown error')
    }
  }
})

async function handleSubmit() {
  if (submitting.value) return

  state.value = 'idle'
  message.value = ''
  submitting.value = true

  try {
    const payload = {
      title: form.value.title,
      content: form.value.content,
      description: form.value.description || undefined,
      status: isContributor.value ? 'draft' : form.value.status,
      send_newsletter: isContributor.value ? false : form.value.send_newsletter,
      tag_names: form.value.tags.map((t) => t.name),
    }

    if (isEditing.value) {
      await updateArticle(route.params.id as string, payload)
      message.value = 'Article updated successfully.'
    } else {
      const article = await createArticle(payload)
      message.value = 'Article created successfully.'
      router.push(`${namespace.value}/articles/${article.id}/edit`)
    }
    state.value = 'success'
    } catch (e: unknown) {
      state.value = 'error'
      message.value = (e instanceof Error ? e.message : 'Something went wrong.') || 'Something went wrong.'
  } finally {
    submitting.value = false
  }
}

async function handleSubmitForReview() {
  if (submitting.value || !articleId.value) return

  state.value = 'idle'
  message.value = ''
  submitting.value = true

  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/admin/articles/${articleId.value}/submit-review`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${store.token}`,
      },
    })
    if (!res.ok) {
      throw new Error(`Failed to submit for review (${res.status})`)
    }
    const data = await res.json()
    form.value.status = data.status
    rejectionFeedback.value = null
    state.value = 'success'
    message.value = 'Submitted for review.'
  } catch (e: unknown) {
    state.value = 'error'
    message.value = (e instanceof Error ? e.message : 'Something went wrong.') || 'Something went wrong.'
  } finally {
    submitting.value = false
  }
}

async function handleSendPreview() {
  if (previewing.value || !isEditing.value) return
  
  state.value = 'idle'
  message.value = ''
  previewing.value = true
  
  try {
    const res = await sendPreviewEmail(route.params.id as string)
    message.value = res.message || 'Preview sent successfully.'
    state.value = 'success'
  } catch (e: unknown) {
    state.value = 'error'
    message.value = (e instanceof Error ? e.message : 'Failed to send preview.') || 'Failed to send preview.'
  } finally {
    previewing.value = false
  }
}

async function handleRestored(article: unknown) {
  const a = article as { title: string; description?: string | null; content: TipTapContent; tags: TagItem[] }
  form.value.title = a.title
  form.value.description = a.description || ''
  form.value.content = a.content || { type: 'doc', content: [{ type: 'paragraph' }] }
  form.value.tags = a.tags || []
  showHistory.value = false
  state.value = 'success'
  message.value = 'Article restored to previous version.'
}

async function handleReassign() {
  if (!selectedAuthorId.value || !articleId.value) return

  const targetUser = activeUsers.value.find((u) => u.id === selectedAuthorId.value)
  if (!targetUser) return

  const ok = await confirm('Reassign Article', `Reassign this article to ${targetUser.email}?`)
  if (!ok) return

  reassigning.value = true
  reassignError.value = ''

  try {
    await reassignArticle(articleId.value, selectedAuthorId.value)
    if (loadedArticle.value) {
      loadedArticle.value.author = { id: selectedAuthorId.value }
    }
    state.value = 'success'
    message.value = `Article reassigned to ${targetUser.email}.`
    selectedAuthorId.value = ''
  } catch (e: unknown) {
    reassignError.value = e instanceof Error ? e.message : 'Failed to reassign article'
  } finally {
    reassigning.value = false
  }
}
</script>
