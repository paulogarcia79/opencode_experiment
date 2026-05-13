<template>
  <div>
    <div class="mb-8">
      <h1 class="text-2xl font-display font-bold text-white">Review Queue</h1>
      <p class="mt-1 text-sm text-slate-500">Articles waiting for editorial review</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Loading review queue...</span>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
      <p class="font-medium text-red-300">{{ error }}</p>
    </div>

    <!-- Empty -->
    <div v-else-if="articles.length === 0" class="px-6 py-16 text-center">
      <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
      </div>
      <p class="text-slate-500 font-mono text-sm">No articles pending review.</p>
    </div>

    <!-- Table -->
    <template v-else>
      <ExpandableTable
        :columns="columns"
        :rows="articles"
        :expanded-ids="expandedIds"
        @expand="handleExpand"
        @collapse="handleCollapse"
      >
        <template #cell-title="{ row }">
          <span class="font-medium text-white">{{ row.title }}</span>
        </template>
        <template #cell-author="{ row }">
          <span class="font-mono text-xs text-slate-400">{{ row.author?.email ?? '—' }}</span>
        </template>
        <template #cell-submitted="{ row }">
          <span class="font-mono text-xs text-slate-500">{{ row.submitted_at ? formatDate(row.submitted_at) : '—' }}</span>
        </template>

        <template #expanded-row="{ row }">
          <div class="bg-white/[0.04] border border-white/5 rounded-lg p-4 space-y-3 text-sm">
            <div v-if="row.description">
              <span class="text-slate-500 text-xs uppercase tracking-wider">Description</span>
              <p class="text-slate-300 mt-1">{{ row.description }}</p>
            </div>
            <div v-if="row.previous_feedback">
              <span class="text-slate-500 text-xs uppercase tracking-wider">Previous Rejection Feedback</span>
              <p class="text-accent-400 mt-1">{{ row.previous_feedback }}</p>
            </div>
            <div class="pt-2">
              <RouterLink
                :to="`${namespace}/articles/${row.id}/edit`"
                class="inline-flex items-center gap-1 text-xs font-medium text-primary-400 hover:text-primary-300 cursor-pointer"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
                Open in full editor
              </RouterLink>
            </div>
          </div>
        </template>

        <template #row-actions="{ row }">
          <div class="flex items-center justify-end gap-2">
            <button
              @click="openApproveDialog(row)"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 hover:bg-emerald-500/15 rounded-md transition-colors duration-200 cursor-pointer"
            >
              Approve
            </button>
            <button
              @click="openRejectModal(row)"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/15 rounded-md transition-colors duration-200 cursor-pointer"
            >
              Reject
            </button>
          </div>
        </template>
      </ExpandableTable>
    </template>

    <!-- Approve Confirmation Dialog -->
    <div v-if="approveTarget" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="approveTarget = null">
      <div class="rounded-xl border border-white/10 bg-surface-900 p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 class="text-lg font-display font-bold text-white mb-2">Approve Article?</h3>
        <div class="space-y-2 text-sm text-slate-400 mb-6">
          <p><span class="text-slate-500">Title:</span> {{ approveTarget.title }}</p>
          <p><span class="text-slate-500">Author:</span> {{ approveTarget.author?.email ?? '—' }}</p>
          <p><span class="text-slate-500">Submitted:</span> {{ approveTarget.submitted_at ? formatDate(approveTarget.submitted_at) : '—' }}</p>
        </div>
        <div class="flex items-center gap-3 justify-end">
          <button
            @click="approveTarget = null"
            class="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="confirmApprove"
            :disabled="actionLoading"
            class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer"
          >
            <span v-if="actionLoading">Approving...</span>
            <span v-else>Approve</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Reject Feedback Modal -->
    <div v-if="rejectTarget" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60" @click.self="rejectTarget = null">
      <div class="rounded-xl border border-white/10 bg-surface-900 p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 class="text-lg font-display font-bold text-white mb-2">Reject Article</h3>
        <p class="text-sm text-slate-400 mb-4">Provide feedback for the contributor.</p>
        <textarea
          v-model="rejectFeedback"
          rows="4"
          placeholder="Explain why the article was rejected..."
          class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-accent-500/50 resize-none mb-4"
        />
        <div class="flex items-center gap-3 justify-end">
          <button
            @click="rejectTarget = null"
            class="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="confirmReject"
            :disabled="actionLoading || !rejectFeedback.trim()"
            class="px-4 py-2 bg-accent-600 hover:bg-accent-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer"
          >
            <span v-if="actionLoading">Rejecting...</span>
            <span v-else>Reject</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, inject } from 'vue'
import { useAdminStore } from '@/stores/admin'
import ExpandableTable from '@/components/ExpandableTable.vue'

const store = useAdminStore()

const refreshReviewCount = inject<() => void>('refreshReviewCount', () => {})

const namespace = computed(() => {
  const role = store.user?.role
  if (role === 'editor') return '/editor'
  return '/admin'
})

const columns = [
  { key: 'title', label: 'Title' },
  { key: 'author', label: 'Author' },
  { key: 'submitted', label: 'Submitted' },
]

const articles = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const expandedIds = ref<string[]>([])
const actionLoading = ref(false)

const approveTarget = ref<any>(null)
const rejectTarget = ref<any>(null)
const rejectFeedback = ref('')

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

function handleExpand(id: string) {
  expandedIds.value = [...expandedIds.value, id]
}

function handleCollapse(id: string) {
  expandedIds.value = expandedIds.value.filter((eid) => eid !== id)
}

async function fetchReviewQueue() {
  loading.value = true
  error.value = ''
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/admin/articles/review`, {
      headers: { Authorization: `Bearer ${store.token}` },
    })
    if (!res.ok) {
      throw new Error(`Failed to load review queue (${res.status})`)
    }
    const data = await res.json()

    // Fetch rejection feedback for each article
    articles.value = data.map((a: any) => ({
      ...a,
      previous_feedback: a.latest_rejection_feedback || null,
    }))
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load review queue'
  } finally {
    loading.value = false
  }
}

function openApproveDialog(row: any) {
  approveTarget.value = row
}

async function confirmApprove() {
  if (!approveTarget.value) return
  actionLoading.value = true
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/admin/articles/${approveTarget.value.id}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${store.token}`,
      },
    })
    if (!res.ok) throw new Error(`Failed to approve (${res.status})`)
    articles.value = articles.value.filter((a) => a.id !== approveTarget.value.id)
    approveTarget.value = null
    refreshReviewCount()
  } catch (e: unknown) {
    alert(e instanceof Error ? e.message : 'Failed to approve')
  } finally {
    actionLoading.value = false
  }
}

function openRejectModal(row: any) {
  rejectTarget.value = row
  rejectFeedback.value = ''
}

async function confirmReject() {
  if (!rejectTarget.value) return
  actionLoading.value = true
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/admin/articles/${rejectTarget.value.id}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${store.token}`,
      },
      body: JSON.stringify({ feedback: rejectFeedback.value }),
    })
    if (!res.ok) throw new Error(`Failed to reject (${res.status})`)
    articles.value = articles.value.filter((a) => a.id !== rejectTarget.value.id)
    rejectTarget.value = null
    refreshReviewCount()
  } catch (e: unknown) {
    alert(e instanceof Error ? e.message : 'Failed to reject')
  } finally {
    actionLoading.value = false
  }
}

onMounted(() => {
  fetchReviewQueue()
})
</script>
