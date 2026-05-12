<template>
  <div class="min-h-screen bg-surface-950">
    <div class="max-w-3xl mx-auto px-6 py-12">
      <input
        v-model="query"
        type="search"
        placeholder="Search articles..."
        class="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
      />

      <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-12">
        <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="font-mono text-sm">Searching...</span>
      </div>

      <div v-else-if="error" class="mt-8 border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-red-300">Search failed</p>
          <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
        </div>
      </div>

      <div v-else-if="!loading && searched && results.length === 0" class="text-center py-12 text-slate-500">
        <p>No results found for "{{ query }}"</p>
      </div>

      <div v-else-if="results.length > 0" class="mt-8 space-y-4">
        <article
          v-for="article in results"
          :key="article.id"
          class="group border border-white/5 rounded-xl p-6 bg-white/[0.02] hover:bg-white/[0.04] transition-colors duration-200"
        >
          <RouterLink :to="`/articles/${article.slug}`" class="block">
            <h2 class="text-xl font-display font-semibold text-white group-hover:text-primary-400 transition-colors">
              {{ article.title }}
            </h2>
            <p v-if="article.description" class="mt-2 text-slate-400 text-sm leading-relaxed">
              {{ article.description }}
            </p>
            <time :datetime="article.published_at" class="mt-3 block text-xs font-mono text-slate-600">
              {{ formatDate(article.published_at) }}
            </time>
          </RouterLink>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSearch } from '@/composables/useSearch'

const route = useRoute()
const router = useRouter()
const { query, loading, results, searched, error } = useSearch()

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(() => {
  if (route.query.q) {
    query.value = route.query.q as string
  }
})

// Sync query back to URL when search is executed
watch(searched, () => {
  if (searched.value && query.value) {
    router.replace({ query: { q: query.value } })
  }
})
</script>
