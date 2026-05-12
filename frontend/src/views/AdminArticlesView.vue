<template>
  <div>
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-display font-bold text-white">Articles</h1>
        <p class="mt-1 text-sm text-slate-500">Manage your blog posts and drafts</p>
      </div>
      <RouterLink
        to="/admin/articles/new"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        New Article
      </RouterLink>
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
    <div v-else class="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden">
      <table class="w-full text-sm">
        <thead class="border-b border-white/5">
          <tr>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Title</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Slug</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Status</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Views</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Email CTR</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Published</th>
            <th class="px-5 py-4 text-right font-medium text-slate-500 text-xs uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr
            v-for="article in articles"
            :key="article.id"
            class="hover:bg-white/[0.02] transition-colors duration-150"
          >
            <td class="px-5 py-4">
              <span class="font-medium text-white">{{ article.title }}</span>
            </td>
            <td class="px-5 py-4 font-mono text-xs text-slate-600">{{ article.slug }}</td>
            <td class="px-5 py-4">
              <span
                :class="[
                  'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                  article.status === 'published'
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-slate-500/10 text-slate-400 border border-slate-500/20',
                ]"
              >
                <span
                  :class="[
                    'w-1.5 h-1.5 rounded-full',
                    article.status === 'published' ? 'bg-emerald-400' : 'bg-slate-500',
                  ]"
                />
                {{ article.status }}
              </span>
            </td>
            <td class="px-5 py-4 font-mono text-xs text-slate-400">
              {{ article.total_views ?? 0 }}
            </td>
            <td class="px-5 py-4 font-mono text-xs text-slate-400">
              {{ article.email_ctr != null ? article.email_ctr.toFixed(1) + '%' : '—' }}
            </td>
            <td class="px-5 py-4 font-mono text-xs text-slate-500">
              {{ article.published_at ? formatDate(article.published_at) : '—' }}
            </td>
            <td class="px-5 py-4 text-right">
              <div class="flex items-center justify-end gap-2">
                <RouterLink
                  :to="`/admin/articles/${article.id}/edit`"
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
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="articles.length === 0" class="px-6 py-16 text-center">
        <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
          <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p class="text-slate-500 font-mono text-sm">No articles yet.</p>
        <p class="text-slate-600 text-sm mt-1">Create your first article to get started.</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchAdminArticles, deleteArticle, fetchArticlePerformance } from '@/composables/useAdminApi'
import type { ArticleWithPerformance } from '@/types'

const articles = ref<ArticleWithPerformance[]>([])
const loading = ref(true)
const error = ref('')

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

async function loadArticles() {
  try {
    const [articlesList, performanceList] = await Promise.all([
      fetchAdminArticles(),
      fetchArticlePerformance(),
    ])

    const perfMap = new Map(performanceList.map((p) => [p.id, p]))
    articles.value = articlesList.map((a) => {
      const perf = perfMap.get(a.id)
      return perf ? { ...a, ...perf } : a
    })
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load articles'
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: string) {
  if (!confirm('Are you sure you want to delete this article?')) return
  try {
    await deleteArticle(id)
    await loadArticles()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to delete article'
  }
}

onMounted(loadArticles)
</script>
