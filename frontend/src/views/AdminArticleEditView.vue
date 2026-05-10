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
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">Title</label>
        <input
          v-model="form.title"
          type="text"
          required
          class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
          placeholder="Article title"
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
          class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
          placeholder="Brief description for the article card"
        />
      </div>

      <!-- Tags -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">
          Tags
          <span class="text-slate-600 font-normal">— max 8</span>
        </label>
        <TagInput v-model="form.tags" />
      </div>

      <!-- Content Editor -->
      <div>
        <label class="block text-sm font-medium text-slate-400 mb-2">Content</label>
        <TipTapEditor :key="editorKey" v-model="form.content" />
      </div>

      <!-- Settings -->
      <div class="flex flex-wrap items-center gap-6 p-5 rounded-xl border border-white/5 bg-white/[0.02]">
        <label class="flex items-center gap-3 cursor-pointer">
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

        <label v-if="form.status === 'published'" class="flex items-center gap-3 cursor-pointer">
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
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-3">
        <button
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
          v-if="isEditing"
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
        <RouterLink
          to="/admin"
          class="px-6 py-2.5 border border-white/10 text-sm font-medium text-slate-400 rounded-lg hover:bg-white/5 hover:text-white transition-all duration-200 cursor-pointer"
        >
          Cancel
        </RouterLink>

        <!-- Auto-save status -->
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import TipTapEditor from '@/components/TipTapEditor.vue'
import TagInput from '@/components/TagInput.vue'
import { createArticle, updateArticle, fetchAdminArticle, sendPreviewEmail } from '@/composables/useAdminApi'
import { useAutoSave } from '@/composables/useAutoSave'

const route = useRoute()
const router = useRouter()
const isEditing = ref(false)

const form = ref({
  title: '',
  description: '',
  content: { type: 'doc', content: [{ type: 'paragraph' }] },
  status: 'draft',
  send_newsletter: true,
  tags: [] as { name: string; slug: string }[],
})

const state = ref<'idle' | 'success' | 'error'>('idle')
const message = ref('')
const submitting = ref(false)
const previewing = ref(false)
const editorKey = ref(0)
const articleId = ref<string | null>(null)

const autosaveForm = computed(() => ({
  title: form.value.title,
  description: form.value.description,
  content: form.value.content,
  tag_names: form.value.tags.map((t) => t.name),
}))

const { status: autosaveStatus, retry: retryAutoSave } = useAutoSave(autosaveForm, articleId, {
  onCreated: (id: string) => {
    router.replace(`/admin/articles/${id}/edit`)
    isEditing.value = true
  },
})

onMounted(async () => {
  const id = route.params.id as string
  if (id && id !== 'new') {
    isEditing.value = true
    try {
      const article = await fetchAdminArticle(id)
      form.value.title = article.title
      form.value.description = article.description || ''
      form.value.content = article.content || { type: 'doc', content: [{ type: 'paragraph' }] }
      form.value.status = article.status
      form.value.send_newsletter = article.send_newsletter
      form.value.tags = article.tags || []
      articleId.value = id
      editorKey.value++
    } catch (e: any) {
      state.value = 'error'
      message.value = 'Failed to load article: ' + e.message
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
      status: form.value.status,
      send_newsletter: form.value.send_newsletter,
      tag_names: form.value.tags.map((t) => t.name),
    }

    if (isEditing.value) {
      await updateArticle(route.params.id as string, payload)
      message.value = 'Article updated successfully.'
    } else {
      const article = await createArticle(payload)
      message.value = 'Article created successfully.'
      router.push(`/admin/articles/${article.id}/edit`)
    }
    state.value = 'success'
  } catch (e: any) {
    state.value = 'error'
    message.value = e.message || 'Something went wrong.'
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
  } catch (e: any) {
    state.value = 'error'
    message.value = e.message || 'Failed to send preview.'
  } finally {
    previewing.value = false
  }
}
</script>
