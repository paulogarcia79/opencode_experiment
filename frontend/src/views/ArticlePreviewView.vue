<template>
  <div class="min-h-screen bg-surface-950">
    <div class="max-w-3xl mx-auto px-6 py-8">
      <!-- Back link -->
      <RouterLink
        to="/contributor"
        class="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer mb-8"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Back to Dashboard
      </RouterLink>

      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
        <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <span class="font-mono text-sm">Loading preview...</span>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="border border-red-500/20 bg-red-500/10 rounded-xl p-6">
        <p class="font-medium text-red-300">{{ error }}</p>
      </div>

      <!-- Article Preview -->
      <article v-else-if="article" class="prose prose-invert prose-lg max-w-none">
        <!-- Title -->
        <h1 class="text-3xl font-display font-bold text-white mb-2">{{ article.title }}</h1>

        <!-- Status badge -->
        <span
          :class="[
            'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium mb-6',
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

        <!-- Rendered content -->
        <div v-if="htmlContent" class="preview-content" v-html="htmlContent" />
        <p v-else class="text-slate-500">No content to preview.</p>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { generateHTML } from '@tiptap/html'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'

const route = useRoute()
const store = useAdminStore()

const article = ref<any>(null)
const htmlContent = ref('')
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const id = route.params.id as string
  try {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
    const res = await fetch(`${API_BASE}/api/admin/articles/${id}`, {
      headers: { Authorization: `Bearer ${store.token}` },
    })
    if (!res.ok) {
      throw new Error(`Failed to load article (${res.status})`)
    }
    const data = await res.json()
    article.value = data

    if (data.content) {
      htmlContent.value = generateHTML(data.content, [
        StarterKit,
        Link,
        Image,
        Table.configure({ resizable: true }),
        TableRow,
        TableCell,
        TableHeader,
      ])
    }
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load article'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.preview-content :deep(h2) {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #fff;
  margin-top: 2rem;
  margin-bottom: 0.75rem;
}
.preview-content :deep(h3) {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 1.25rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}
.preview-content :deep(p) {
  color: #94a3b8;
  line-height: 1.8;
  margin-bottom: 1.25rem;
}
.preview-content :deep(a) {
  color: #7C3AED;
  text-decoration: underline;
}
.preview-content :deep(blockquote) {
  border-left: 3px solid #7C3AED;
  padding-left: 1rem;
  color: #94a3b8;
  font-style: italic;
}
.preview-content :deep(code) {
  font-family: 'JetBrains Mono', monospace;
  background: rgba(255, 255, 255, 0.05);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875em;
}
.preview-content :deep(pre) {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 0.5rem;
  padding: 1rem;
  overflow-x: auto;
}
.preview-content :deep(pre code) {
  background: none;
  padding: 0;
}
.preview-content :deep(img) {
  max-width: 100%;
  border-radius: 0.5rem;
  margin: 1rem 0;
}
.preview-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}
.preview-content :deep(th) {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-weight: 600;
}
.preview-content :deep(td) {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 0.75rem;
}
</style>
