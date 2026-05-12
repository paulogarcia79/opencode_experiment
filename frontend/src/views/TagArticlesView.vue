<template>
  <div class="min-h-screen bg-surface-950">
    <!-- Header -->
    <header class="border-b border-white/5 bg-surface-950/80 backdrop-blur-md sticky top-0 z-50">
      <div class="max-w-4xl mx-auto px-6 py-5">
        <div class="flex items-center justify-between">
          <RouterLink to="/" class="group flex items-center gap-3 cursor-pointer">
            <div class="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shadow-lg shadow-primary-600/20">
              <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-display font-semibold text-white tracking-tight group-hover:text-primary-400 transition-colors duration-200">
                Tech & Games Blog
              </h1>
            </div>
          </RouterLink>
        </div>
      </div>
    </header>

    <!-- Tag Header -->
    <section class="border-b border-white/5">
      <div class="max-w-4xl mx-auto px-6 py-12">
        <div class="flex items-center gap-3 mb-4">
          <RouterLink
            to="/"
            class="inline-flex items-center gap-2 text-sm font-mono text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to all articles
          </RouterLink>
        </div>
        <h2 class="text-3xl font-display font-bold text-white tracking-tight">
          {{ tagName }}
        </h2>
        <p class="mt-2 text-slate-400 text-sm">
          {{ articles.length }} article{{ articles.length === 1 ? '' : 's' }} tagged
        </p>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Loading articles...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-4xl mx-auto px-6 py-20">
      <div class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-red-300">Error loading tag</p>
          <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Articles List -->
    <main v-else class="max-w-4xl mx-auto px-6 py-12">
      <div v-if="articles.length === 0" class="text-center py-20">
        <div class="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
        <p class="text-slate-500 font-mono text-sm">No articles found with this tag.</p>
      </div>

      <div v-else class="space-y-6">
        <article
          v-for="(article, index) in articles"
          :key="article.id"
          class="group relative"
          :style="{ animationDelay: `${index * 80}ms` }"
        >
          <RouterLink
            :to="`/articles/${article.slug}`"
            class="block p-6 rounded-xl border border-white/5 bg-white/[0.02] hover:bg-white/[0.04] hover:border-primary-500/20 transition-all duration-300 cursor-pointer"
          >
            <div class="absolute inset-0 rounded-xl bg-primary-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
            
            <div class="relative">
              <h3 class="text-xl font-display font-semibold text-white group-hover:text-primary-400 transition-colors duration-200">
                {{ article.title }}
              </h3>
              <div class="mt-3 flex flex-wrap items-center gap-3 text-sm text-slate-500">
                <time :datetime="article.published_at ?? undefined" class="font-mono text-xs">{{ formatDate(article.published_at ?? '') }}</time>
                <span class="w-1 h-1 rounded-full bg-slate-600" />
                <span class="font-mono text-xs">{{ formatReadingTime(estimateReadingTime(article.content)) }}</span>
              </div>
              <p v-if="article.description" class="mt-4 text-slate-400 leading-relaxed line-clamp-2">
                {{ article.description }}
              </p>
            </div>
          </RouterLink>
        </article>
      </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-white/5 mt-20">
      <div class="max-w-4xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded bg-primary-600 flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span class="text-sm text-slate-500">Tech & Games Blog</span>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { estimateReadingTime, formatReadingTime } from '@/composables/useReadingTime'
import type { Article, TagArticlesResponse } from '@/types'

const route = useRoute()
const tagName = ref('')
const articles = ref<Article[]>([])
const loading = ref(true)
const error = ref('')

function formatDate(dateStr: string): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(async () => {
  try {
    const slug = route.params.slug as string
    const res = await fetch(`/api/tags/${slug}`)
    if (!res.ok) {
      if (res.status === 404) {
        error.value = 'Tag not found'
      } else {
        error.value = 'Failed to load tag'
      }
      return
    }
    const data = await res.json() as TagArticlesResponse
    tagName.value = data.name
    articles.value = data.articles || []
  } catch (e: unknown) {
    error.value = (e instanceof Error ? e.message : 'Failed to load tag') || 'Failed to load tag'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
article {
  animation: slideUp 0.5s ease-out both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(16px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
