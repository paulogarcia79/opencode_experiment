<template>
  <div>
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-display font-bold text-white">My Articles</h1>
        <p class="mt-1 text-sm text-slate-500">
          Manage your drafts and published posts
          <span
            v-if="attentionCount > 0"
            class="inline-flex items-center gap-1 ml-2 px-2 py-0.5 rounded-full bg-accent-500/10 text-accent-400 text-xs font-medium border border-accent-500/20"
          >
            {{ attentionCount }} need{{ attentionCount === 1 ? 's' : '' }} attention
          </span>
        </p>
      </div>
      <RouterLink
        to="/contributor/articles/new"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Article
      </RouterLink>
    </div>

    <!-- Filter & Search -->
    <div class="flex items-center gap-3 mb-6 flex-wrap">
      <div class="flex items-center gap-1">
        <button
          v-for="tab in filterTabs"
          :key="tab.value"
          @click="setFilter(tab.value)"
          :class="[
            'px-3 py-1.5 text-sm rounded-lg transition-colors duration-200 cursor-pointer',
            statusFilter === tab.value
              ? 'bg-primary-600/20 text-primary-400'
              : 'text-slate-500 hover:text-white hover:bg-white/5',
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
      <div class="relative">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search articles..."
          class="pl-9 pr-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-sm text-slate-300 placeholder-slate-500 focus:outline-none focus:border-primary-500/50 focus:bg-white/[0.07] transition-colors duration-200 w-56"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Loading articles...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
      <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <p class="font-medium text-red-300">Failed to load articles</p>
        <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
      </div>
    </div>

    <!-- Card Grid -->
    <template v-else>
      <div v-if="articles.length === 0" class="px-6 py-16 text-center">
        <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
          <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-slate-500 font-mono text-sm">No articles yet.</p>
        <p class="text-slate-600 text-sm mt-1">Create your first article to get started.</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="article in articles"
          :key="article.id"
          class="rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] transition-colors duration-200 p-5 flex flex-col gap-3"
        >
          <!-- Title -->
          <h3 class="font-medium text-white leading-snug line-clamp-2">{{ article.title }}</h3>

          <!-- Status Badge -->
          <div class="flex items-center gap-2 flex-wrap">
            <span
              :class="[
                'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                article.status === 'published'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                  : article.status === 'pending_review'
                    ? 'bg-accent-500/10 text-accent-400 border border-accent-500/20'
                    : 'bg-slate-500/10 text-slate-400 border border-slate-500/20',
              ]"
            >
              <span
                :class="[
                  'w-1.5 h-1.5 rounded-full',
                  article.status === 'published' ? 'bg-emerald-400' : article.status === 'pending_review' ? 'bg-accent-400' : 'bg-slate-500',
                ]"
              />
              {{ article.status }}
            </span>
            <span
              v-if="article.has_been_rejected"
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-accent-500/10 text-accent-400 text-xs font-medium border border-accent-500/20"
              :title="article.latest_rejection_feedback ?? undefined"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Rejected
            </span>
          </div>

          <!-- Meta -->
          <div class="flex items-center gap-4 text-xs text-slate-500">
            <span>{{ article.published_at ? formatDate(article.published_at) : '—' }}</span>
            <span>{{ article.total_views ?? 0 }} views</span>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2 mt-auto pt-3 border-t border-white/5">
            <RouterLink
              :to="`/contributor/articles/${article.id}/preview`"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white border border-white/10 hover:border-white/20 rounded-md transition-colors duration-200 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              Read
            </RouterLink>
            <RouterLink
              :to="`/contributor/articles/${article.id}/edit`"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-primary-400 hover:text-primary-300 bg-primary-500/10 hover:bg-primary-500/15 rounded-md transition-colors duration-200 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </RouterLink>
            <button
              @click="handleDelete(article.id)"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/15 rounded-md transition-colors duration-200 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete
            </button>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="hasMore" class="flex justify-center mt-6">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="px-6 py-2.5 bg-white/5 hover:bg-white/10 text-slate-300 text-sm rounded-lg transition-colors duration-200 cursor-pointer disabled:opacity-50"
        >
          <span v-if="loadingMore">Loading...</span>
          <span v-else>Load More</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import type { ArticleWithPerformance } from '@/types'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const store = useAdminStore()
const { confirm } = useConfirm()
const { show: showToast } = useToast()

const PAGE_SIZE = 20

const articles = ref<ArticleWithPerformance[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const error = ref('')
const hasMore = ref(false)
const totalLoaded = ref(0)

const statusFilter = ref(route.query.status as string || '')
const searchQuery = ref(route.query.search as string || '')

let searchTimer: ReturnType<typeof setTimeout> | null = null

const filterTabs = [
  { label: 'All', value: '' },
  { label: 'Drafts', value: 'draft' },
  { label: 'Published', value: 'published' },
  { label: 'Pending Review', value: 'pending_review' },
]

const attentionCount = computed(() =>
  articles.value.filter((a) => a.has_been_rejected).length,
)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

async function fetchArticles(reset = false) {
  if (reset) {
    loading.value = true
    error.value = ''
    totalLoaded.value = 0
  }

  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const params = new URLSearchParams()
    params.set('skip', reset ? '0' : String(totalLoaded.value))
    params.set('limit', String(PAGE_SIZE))
    params.set('sort', 'updated_at')
    params.set('order', 'desc')
    if (statusFilter.value) {
      params.set('status', statusFilter.value)
    }

    const res = await fetch(`${API_BASE}/api/admin/articles?${params}`, {
      headers: { Authorization: `Bearer ${store.token}` },
    })
    if (!res.ok) {
      throw new Error(`Failed to load articles (${res.status})`)
    }
    const data = await res.json()

    if (reset) {
      articles.value = data
    } else {
      articles.value = [...articles.value, ...data]
    }
    totalLoaded.value = reset ? data.length : totalLoaded.value + data.length
    hasMore.value = data.length === PAGE_SIZE
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load articles'
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

async function loadMore() {
  loadingMore.value = true
  await fetchArticles(false)
}

function setFilter(value: string) {
  statusFilter.value = value
  updateQueryParams()
}

function updateQueryParams() {
  const query: Record<string, string | undefined> = {}
  if (statusFilter.value) query.status = statusFilter.value
  if (searchQuery.value) query.search = searchQuery.value
  router.replace({ query })
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    updateQueryParams()
    fetchArticles(true)
  }, 300)
}

async function handleDelete(articleId: string) {
  const ok = await confirm('Delete Article', 'Are you sure you want to delete this article?', 'danger')
  if (!ok) return
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/articles/${articleId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${store.token}` },
    })
    if (!res.ok) {
      throw new Error(`Failed to delete (${res.status})`)
    }
    articles.value = articles.value.filter((a) => a.id !== articleId)
  } catch (e: unknown) {
    showToast(e instanceof Error ? e.message : 'Failed to delete article', 'error')
  }
}

watch([statusFilter], () => {
  fetchArticles(true)
})

watch(searchQuery, () => {
  onSearch()
})

onMounted(() => {
  fetchArticles(true)
})
</script>
