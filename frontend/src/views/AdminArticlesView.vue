<template>
  <div>
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-display font-bold text-white">Articles</h1>
        <p class="mt-1 text-sm text-slate-500">Manage your blog posts and drafts</p>
      </div>
      <RouterLink
        :to="`${namespace}/articles/new`"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Article
      </RouterLink>
    </div>

    <!-- Filter Tabs -->
    <div class="flex items-center gap-1 mb-6 flex-wrap">
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

    <!-- Articles Table -->
    <template v-else>
      <ExpandableTable
        :columns="tableColumns"
        :rows="articlesWithPerformance"
        :expanded-ids="expandedIds"
        :sort-column="sortColumn"
        :sort-order="sortOrder"
        @expand="handleExpand"
        @collapse="handleCollapse"
        @sort="handleSort"
      >
        <!-- Cell slots -->
        <template #cell-title="{ row }">
          <span class="font-medium text-white">{{ row.title }}</span>
        </template>
        <template #cell-author="{ row }">
          <span class="font-mono text-xs text-slate-400">{{ row.author?.email ?? '—' }}</span>
        </template>
        <template #cell-status="{ row }">
          <span
            :class="[
              'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap',
              row.status === 'published'
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : row.status === 'pending_review'
                  ? 'bg-accent-500/10 text-accent-400 border border-accent-500/20'
                  : 'bg-slate-500/10 text-slate-400 border border-slate-500/20',
            ]"
          >
            <span
              :class="[
                'w-1.5 h-1.5 rounded-full',
                row.status === 'published' ? 'bg-emerald-400' : row.status === 'pending_review' ? 'bg-accent-400' : 'bg-slate-500',
              ]"
            />
            {{ row.status }}
          </span>
        </template>

        <!-- Expanded row detail card -->
        <template #expanded-row="{ row }">
          <div class="bg-white/[0.04] border border-white/5 rounded-lg p-4 inline-flex flex-wrap gap-x-8 gap-y-2 text-sm">
            <div class="flex flex-col">
              <span class="text-slate-500 text-xs uppercase tracking-wider">Published</span>
              <span class="font-mono text-slate-300">{{ row.published_at ? formatDate(row.published_at) : '—' }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-slate-500 text-xs uppercase tracking-wider">Views</span>
              <span class="font-mono text-slate-300">{{ row.total_views ?? 0 }}</span>
            </div>
            <div class="flex flex-col">
              <span class="text-slate-500 text-xs uppercase tracking-wider">Email CTR</span>
              <span class="font-mono text-slate-300">{{ row.email_ctr != null ? row.email_ctr.toFixed(1) + '%' : '—' }}</span>
            </div>
          </div>
        </template>

        <!-- Row actions -->
        <template #row-actions="{ row }">
          <div class="flex items-center justify-end gap-2">
            <RouterLink
              v-if="row._canEdit"
              :to="`${namespace}/articles/${row.id}/edit`"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-primary-400 hover:text-primary-300 bg-primary-500/10 hover:bg-primary-500/15 rounded-md transition-colors duration-200 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
              Edit
            </RouterLink>
            <button
              v-if="row._canDelete"
              @click="handleDelete(row.id)"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/15 rounded-md transition-colors duration-200 cursor-pointer"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Delete
            </button>
            <span
              v-if="!row._canEdit && !row._canDelete"
              class="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium text-slate-500 bg-slate-500/10 rounded-md"
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
              View Only
            </span>
          </div>
        </template>
      </ExpandableTable>

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
import ExpandableTable from '@/components/ExpandableTable.vue'
import { useAdminStore } from '@/stores/admin'
import type { ArticleWithPerformance } from '@/types'
import { useConfirm } from '@/composables/useConfirm'
import { useToast } from '@/composables/useToast'

const route = useRoute()
const router = useRouter()
const store = useAdminStore()
const { confirm } = useConfirm()
const { show: showToast } = useToast()

const namespace = computed(() => {
  const role = store.user?.role
  if (role === 'editor') return '/editor'
  if (role === 'contributor') return '/contributor'
  return '/admin'
})

const PAGE_SIZE = 20

const articles = ref<ArticleWithPerformance[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const error = ref('')
const hasMore = ref(false)
const totalLoaded = ref(0)

const statusFilter = ref(route.query.status as string || '')
const sortColumn = ref(route.query.sort as string || 'updated_at')
const sortOrder = ref(route.query.order as string || 'desc')
const expandedIds = ref<string[]>([])

const filterTabs = [
  { label: 'All', value: '' },
  { label: 'Drafts', value: 'draft' },
  { label: 'Published', value: 'published' },
  { label: 'Pending Review', value: 'pending_review' },
]

const tableColumns = [
  { key: 'title', label: 'Title', sortable: true },
  { key: 'author', label: 'Author', sortable: false },
  { key: 'status', label: 'Status', sortable: true },
]

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

function canEditArticle(article: ArticleWithPerformance): boolean {
  const user = store.user
  if (!user) return false
  const allowed = user.role === 'admin' || user.role === 'editor'
    ? ['create', 'edit_own', 'edit_others', 'delete', 'publish']
    : user.role === 'contributor'
      ? ['create', 'edit_own']
      : []
  const isOwn = article.author?.id === user.id
  if (isOwn) return allowed.includes('edit_own')
  return allowed.includes('edit_others')
}

function canDeleteArticle(article: ArticleWithPerformance): boolean {
  const user = store.user
  if (!user) return false
  if (user.role === 'contributor') {
    return article.author?.id === user.id
  }
  return user.role === 'admin' || user.role === 'editor'
}

const articlesWithPerformance = computed(() =>
  articles.value.map((a) => ({
    ...a,
    _canEdit: canEditArticle(a),
    _canDelete: canDeleteArticle(a),
  })),
)

async function fetchArticles(reset = false) {
  if (reset) {
    loading.value = true
    error.value = ''
  }

  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const params = new URLSearchParams()
    params.set('skip', reset ? '0' : String(totalLoaded.value))
    params.set('limit', String(PAGE_SIZE))
    params.set('sort', sortColumn.value)
    params.set('order', sortOrder.value)
    if (statusFilter.value) {
      params.set('status', statusFilter.value)
    }

    const res = await fetch(`${API_BASE}/api/admin/articles?${params}`, {
      headers: { Authorization: `Bearer ${store.token}` },
    })
    if (!res.ok) {
      throw new Error(`Failed to load articles (${res.status})`)
    }
    const data: ArticleWithPerformance[] = await res.json()

    if (reset) {
      articles.value = data
      totalLoaded.value = data.length
    } else {
      articles.value = [...articles.value, ...data]
      totalLoaded.value += data.length
    }
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
  router.replace({ query: { ...route.query, status: value || undefined } })
}

function handleSort(col: string) {
  if (sortColumn.value === col) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = col
    sortOrder.value = 'asc'
  }
  router.replace({
    query: {
      ...route.query,
      sort: sortColumn.value,
      order: sortOrder.value,
    },
  })
}

function handleExpand(id: string) {
  expandedIds.value = [...expandedIds.value, id]
}

function handleCollapse(id: string) {
  expandedIds.value = expandedIds.value.filter((eid) => eid !== id)
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

watch([statusFilter, sortColumn, sortOrder], () => {
  totalLoaded.value = 0
  fetchArticles(true)
})

onMounted(() => {
  fetchArticles(true)
})
</script>
