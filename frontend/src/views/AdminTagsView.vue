<template>
  <div>
    <!-- Page Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-display font-bold text-white">Tags</h1>
      <p class="mt-1 text-sm text-slate-500">Manage article tags</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Loading tags...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
      <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <p class="font-medium text-red-300">Error loading tags</p>
        <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
      </div>
    </div>

    <!-- Tags Table -->
    <div v-else class="border border-white/5 rounded-xl overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b border-white/5 bg-white/[0.02]">
            <th class="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Name</th>
            <th class="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Slug</th>
            <th class="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Articles</th>
            <th class="text-left px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Created</th>
            <th class="text-right px-4 py-3 text-xs font-medium text-slate-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="tag in tags" :key="tag.id" class="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
            <td class="px-4 py-3 text-sm text-white">{{ tag.name }}</td>
            <td class="px-4 py-3 text-sm font-mono text-slate-500">{{ tag.slug }}</td>
            <td class="px-4 py-3 text-sm text-slate-400">{{ tag.article_count }}</td>
            <td class="px-4 py-3 text-sm text-slate-500">{{ formatDate(tag.created_at) }}</td>
            <td class="px-4 py-3 text-right">
              <button
                class="text-red-400 hover:text-red-300 transition-colors"
                title="Delete"
                @click="confirmDelete(tag)"
              >
                <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="tags.length === 0" class="text-center py-12">
        <p class="text-slate-500 font-mono text-sm">No tags yet.</p>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteDialog" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div class="bg-surface-900 border border-white/10 rounded-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-display font-semibold text-white mb-2">Delete Tag</h3>
        <p class="text-slate-400 text-sm mb-6">
          <span v-if="(tagToDelete?.article_count ?? 0) > 0">
            This tag is used by {{ tagToDelete!.article_count }} article{{ tagToDelete!.article_count === 1 ? '' : 's' }}. Deleting it will remove the tag from those articles.
          </span>
          <span v-else>
            Are you sure you want to delete "{{ tagToDelete!.name }}"? This action cannot be undone.
          </span>
        </p>
        <div class="flex items-center justify-end gap-3">
          <button
            class="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
            @click="showDeleteDialog = false"
          >
            Cancel
          </button>
          <button
            class="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-sm font-medium rounded-lg transition-colors"
            @click="executeDelete"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAuthHeaders } from '@/composables/useAdminApi'

interface Tag {
  id: string
  name: string
  slug: string
  article_count: number
  created_at: string
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const tags = ref<Tag[]>([])
const loading = ref(true)
const error = ref('')
const showDeleteDialog = ref(false)
const tagToDelete = ref<Tag | null>(null)

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

async function fetchTags() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetch(`${API_BASE}/api/admin/tags`, {
      headers: getAuthHeaders(),
    })
    if (!res.ok) throw new Error('Failed to load tags')
    tags.value = await res.json()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load tags'
  } finally {
    loading.value = false
  }
}

function confirmDelete(tag: Tag) {
  tagToDelete.value = tag
  showDeleteDialog.value = true
}

async function executeDelete() {
  if (!tagToDelete.value) return
  try {
    const res = await fetch(`${API_BASE}/api/admin/tags/${tagToDelete.value.id}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({ detail: 'Delete failed' }))
      const detail = data.detail
      throw new Error(typeof detail === 'string' ? detail : detail?.detail || 'Delete failed')
    }
    showDeleteDialog.value = false
    tagToDelete.value = null
    await fetchTags()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Delete failed'
    showDeleteDialog.value = false
  }
}

onMounted(fetchTags)
</script>
