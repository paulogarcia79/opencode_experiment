<template>
  <div class="min-h-screen bg-surface-950">
    <!-- Header -->
    <header class="border-b border-white/5 bg-surface-950/80 backdrop-blur-md">
      <div class="max-w-3xl mx-auto px-6 py-5">
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
    </header>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-32">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Loading article...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="max-w-3xl mx-auto px-6 py-20">
      <div class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
        <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <p class="font-medium text-red-300">Error loading article</p>
          <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Article Content -->
    <article v-else class="max-w-3xl mx-auto px-6 py-12">
      <!-- Article Header -->
      <header class="mb-12">
        <h1 class="text-3xl sm:text-4xl font-display font-bold text-white tracking-tight leading-tight">
          {{ loadedArticle.title }}
        </h1>
        <div class="mt-6 flex flex-wrap items-center gap-4 text-sm text-slate-500">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-full bg-primary-600/20 flex items-center justify-center">
              <svg class="w-4 h-4 text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <span class="font-medium text-slate-400">Author</span>
          </div>
          <span class="w-1 h-1 rounded-full bg-slate-600" />
          <time :datetime="loadedArticle.published_at ?? undefined" class="font-mono text-xs">{{ formatDate(loadedArticle.published_at ?? '') }}</time>
          <span class="w-1 h-1 rounded-full bg-slate-600" />
          <span class="font-mono text-xs">{{ formatReadingTime(estimateReadingTime(loadedArticle.content)) }}</span>
          <span class="w-1 h-1 rounded-full bg-slate-600" />
          <span class="font-mono text-xs">{{ loadedArticle.slug }}</span>
        </div>

        <!-- Tags -->
        <div v-if="loadedArticle.tags && loadedArticle.tags.length > 0" class="mt-4 flex flex-wrap gap-2">
          <RouterLink
            v-for="tag in loadedArticle.tags"
            :key="tag.slug"
            :to="`/tags/${tag.slug}`"
            class="inline-flex items-center px-2.5 py-0.5 rounded-md border border-white/10 text-xs font-mono text-slate-400 hover:border-primary-500/30 hover:text-primary-400 transition-colors cursor-pointer"
          >
            {{ tag.name }}
          </RouterLink>
        </div>
      </header>

      <!-- Article Body -->
      <div class="prose prose-invert prose-slate max-w-none article-content">
        <TipTapRenderer :content="loadedArticle.content" />
      </div>

      <!-- Share Section -->
      <div class="mt-12 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm text-slate-500">Share this article</span>
          <ShareButtons
            :url="shareUrl"
            :title="loadedArticle.title"
            :description="loadedArticle.description || ''"
          />
        </div>
      </div>

      <!-- Newsletter Section -->
      <footer v-if="!store.token" class="mt-16 pt-12 border-t border-white/5">
        <div class="rounded-xl border border-white/5 bg-white/[0.02] p-8">
          <NewsletterForm />
        </div>
      </footer>
    </article>

    <!-- Footer -->
    <footer class="border-t border-white/5 mt-12">
      <div class="max-w-3xl mx-auto px-6 py-8 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 rounded bg-primary-600 flex items-center justify-center">
            <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span class="text-sm text-slate-500">Tech & Games Blog</span>
        </div>
        <RouterLink
          to="/"
          class="text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200 cursor-pointer"
        >
          All articles
        </RouterLink>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { fetchArticle } from '@/composables/useApi'
import { useHead } from '@/composables/useHead'
import { estimateReadingTime, formatReadingTime } from '@/composables/useReadingTime'
import TipTapRenderer from '@/components/TipTapRenderer.vue'
import NewsletterForm from '@/components/NewsletterForm.vue'
import ShareButtons from '@/components/ShareButtons.vue'
import type { Article } from '@/types'

const route = useRoute()
const store = useAdminStore()
const article = ref<Article | null>(null)
const loading = ref(true)
const error = ref('')

const shareUrl = computed(() => {
  if (!article.value) return ''
  return `${window.location.origin}/articles/${article.value.slug}`
})

const loadedArticle = computed(() => article.value!)

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
    const fetched = await fetchArticle(route.params.slug as string)
    article.value = fetched
    
    // Track view in the background
    fetch(`/api/articles/${fetched.slug}/view`, { method: 'POST' }).catch(console.error)

    const baseUrl = window.location.origin
    useHead({
      title: fetched.title,
      description: fetched.description || undefined,
      canonical: `${baseUrl}/articles/${fetched.slug}`,
      ogTitle: fetched.title,
      ogDescription: fetched.description || undefined,
      ogType: 'article',
      ogUrl: `${baseUrl}/articles/${fetched.slug}`,
      twitterTitle: fetched.title,
      twitterDescription: fetched.description || undefined,
      jsonLd: {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: fetched.title,
        description: fetched.description || undefined,
        datePublished: fetched.published_at ?? undefined,
        dateModified: fetched.updated_at,
        author: { '@type': 'Organization', name: 'Tech & Games Blog' },
        publisher: { '@type': 'Organization', name: 'Tech & Games Blog' },
        mainEntityOfPage: `${baseUrl}/articles/${fetched.slug}`,
      },
    })
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load article'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.article-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.75rem;
  margin: 1.5rem 0;
}

.article-content :deep(table) {
  border-collapse: collapse;
  margin: 1.5rem 0;
  width: 100%;
}
.article-content :deep(td),
.article-content :deep(th) {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 0.75rem;
  min-width: 100px;
}
.article-content :deep(th) {
  background: rgba(124, 58, 237, 0.1);
  font-weight: 600;
}
.article-content :deep(td) {
  background: rgba(255, 255, 255, 0.02);
}
</style>
