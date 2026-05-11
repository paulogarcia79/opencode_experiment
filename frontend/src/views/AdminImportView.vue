<template>
  <div>
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-display font-bold text-white">Import Articles</h1>
        <p class="mt-1 text-sm text-slate-500">Upload Markdown files to create articles</p>
      </div>
    </div>

    <!-- Drop Zone -->
    <div
      v-if="!imported"
      class="border-2 border-dashed rounded-xl p-12 text-center transition-colors duration-200"
      :class="isDragging ? 'border-primary-500 bg-primary-500/10' : 'border-white/10 bg-white/[0.02]'"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3" />
        </svg>
      </div>
      <p class="text-slate-400 font-mono text-sm mb-2">Drag & drop Markdown files here</p>
      <p class="text-slate-600 text-sm mb-6">or</p>
      <button
        @click="fileInput?.click()"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
        Browse files
      </button>
      <input
        ref="fileInput"
        type="file"
        accept=".md"
        multiple
        class="hidden"
        @change="handleFileChange"
      />
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Importing...</span>
    </div>

    <!-- Error State -->
    <div v-if="error && !imported" class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4 mt-6">
      <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <p class="font-medium text-red-300">Import failed</p>
        <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
      </div>
    </div>

    <!-- Results -->
    <div v-if="imported" class="space-y-6">
      <!-- Summary -->
      <div class="grid grid-cols-2 gap-4">
        <div class="rounded-xl border border-white/5 bg-white/[0.02] p-6">
          <p class="text-sm text-slate-500 font-mono">Imported</p>
          <p class="text-3xl font-display font-bold text-emerald-400 mt-1">{{ result?.successes.length ?? 0 }}</p>
        </div>
        <div class="rounded-xl border border-white/5 bg-white/[0.02] p-6">
          <p class="text-sm text-slate-500 font-mono">Failed</p>
          <p class="text-3xl font-display font-bold text-red-400 mt-1">{{ result?.errors.length ?? 0 }}</p>
        </div>
      </div>

      <!-- Success List -->
      <div v-if="result && result.successes.length > 0" class="rounded-xl border border-white/5 bg-white/[0.02] p-6">
        <h2 class="text-sm font-mono text-slate-500 mb-4">Successfully imported</h2>
        <ul class="space-y-2">
          <li v-for="item in result.successes" :key="item.id">
            <RouterLink
              :to="`/admin/articles/${item.id}/edit`"
              class="text-primary-400 hover:text-primary-300 transition-colors duration-200"
            >
              {{ item.title }}
            </RouterLink>
          </li>
        </ul>
      </div>

      <!-- Error List -->
      <div v-if="result && result.errors.length > 0" class="rounded-xl border border-white/5 bg-white/[0.02]">
        <button
          @click="showErrors = !showErrors"
          class="w-full flex items-center justify-between p-6 text-left cursor-pointer"
        >
          <h2 class="text-sm font-mono text-slate-500">Failed imports</h2>
          <svg
            class="w-4 h-4 text-slate-500 transition-transform duration-200"
            :class="showErrors ? 'rotate-180' : ''"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        <div v-if="showErrors" class="px-6 pb-6 space-y-3">
          <div
            v-for="err in result.errors"
            :key="err.filename"
            class="flex items-start gap-3 p-3 rounded-lg bg-red-500/5 border border-red-500/10"
          >
            <svg class="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p class="text-sm text-white font-mono">{{ err.filename }}</p>
              <p class="text-xs text-red-400/80 mt-0.5">{{ err.error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Back to Articles -->
      <RouterLink
        to="/admin"
        class="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-primary-400 transition-colors duration-200"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-6 14h14" />
        </svg>
        Back to Articles
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { importMarkdownFiles, type ImportResult } from '@/composables/useMarkdownImport'

const fileInput = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const loading = ref(false)
const error = ref('')
const imported = ref(false)
const result = ref<ImportResult | null>(null)
const showErrors = ref(false)

async function processFiles(files: FileList | File[]) {
  const mdFiles = Array.from(files).filter(f => f.name.endsWith('.md'))
  if (mdFiles.length === 0) return

  loading.value = true
  error.value = ''
  imported.value = false

  try {
    result.value = await importMarkdownFiles(mdFiles)
    imported.value = true
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Import failed'
  } finally {
    loading.value = false
  }
}

function handleDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files) processFiles(files)
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const files = input.files
  if (files) processFiles(files)
  input.value = ''
}
</script>
