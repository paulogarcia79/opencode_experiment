<template>
  <div>
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-display font-bold text-white">Media Library</h1>
        <p class="mt-1 text-sm text-slate-500">Manage your uploaded images</p>
      </div>
      <button
        @click="openUpload"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Upload Image
      </button>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
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
      <span class="font-mono text-sm">Loading images...</span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="border border-red-500/20 bg-red-500/10 rounded-xl p-6 flex items-start gap-4">
      <div class="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
        <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <div>
        <p class="font-medium text-red-300">Failed to load images</p>
        <p class="text-sm text-red-400/80 mt-1">{{ error }}</p>
      </div>
    </div>

    <!-- Image Grid -->
    <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <div
        v-for="image in images"
        :key="image.id"
        class="group rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden hover:border-white/10 transition-all duration-200"
      >
        <!-- Image Thumbnail -->
        <div class="aspect-square bg-surface-900 relative overflow-hidden">
          <img
            :src="image.url"
            :alt="image.original_name"
            class="w-full h-full object-cover"
            loading="lazy"
          />
          <!-- Hover Overlay -->
          <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center gap-2">
            <button
              @click="copyUrl(image.url)"
              class="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white transition-colors duration-200 cursor-pointer"
              title="Copy URL"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </button>
            <button
              @click="confirmDelete(image)"
              class="p-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-400 transition-colors duration-200 cursor-pointer"
              title="Delete"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>
        <!-- Image Info -->
        <div class="p-3">
          <p class="text-xs text-white truncate" :title="image.original_name">{{ image.original_name }}</p>
          <p class="text-xs text-slate-600 mt-0.5">{{ formatSize(image.size_bytes) }}</p>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && !error && images.length === 0" class="px-6 py-16 text-center">
      <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <p class="text-slate-500 font-mono text-sm">No images yet.</p>
      <p class="text-slate-600 text-sm mt-1">Upload your first image to get started.</p>
    </div>

    <!-- Copy Toast -->
    <div
      v-if="copyToast"
      class="fixed bottom-6 right-6 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium flex items-center gap-2 transition-all duration-300"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      URL copied to clipboard
    </div>

    <!-- Delete Confirmation Dialog -->
    <div
      v-if="deleteDialog.open"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      @click.self="deleteDialog.open = false"
    >
      <div class="bg-surface-900 border border-white/10 rounded-2xl p-6 max-w-sm w-full mx-4 shadow-2xl">
        <h3 class="text-lg font-semibold text-white mb-2">Delete Image</h3>
        <p class="text-sm text-slate-400 mb-6">
          Are you sure you want to delete <span class="text-white font-medium">{{ deleteDialog.image?.original_name }}</span>? This action cannot be undone.
        </p>
        <div class="flex items-center justify-end gap-3">
          <button
            @click="deleteDialog.open = false"
            class="px-4 py-2 text-sm font-medium text-slate-400 hover:text-white transition-colors duration-200 cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="executeDelete"
            :disabled="deleteDialog.loading"
            class="px-4 py-2 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors duration-200 cursor-pointer"
          >
            {{ deleteDialog.loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchAdminImages, deleteImage } from '@/composables/useAdminApi'
import { uploadImage } from '@/composables/useImageUpload'

interface ImageAsset {
  id: string
  url: string
  original_name: string
  size_bytes: number
  mime_type: string
  created_at: string
}

const images = ref<ImageAsset[]>([])
const loading = ref(true)
const error = ref('')
const copyToast = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const deleteDialog = ref({
  open: false,
  loading: false,
  image: null as ImageAsset | null,
})

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

async function loadImages() {
  try {
    loading.value = true
    error.value = ''
    images.value = await fetchAdminImages()
  } catch (e: any) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function openUpload() {
  fileInput.value?.click()
}

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  try {
    await uploadImage(file)
    await loadImages()
  } catch (e: any) {
    error.value = e.message
  } finally {
    input.value = ''
  }
}

async function copyUrl(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    copyToast.value = true
    setTimeout(() => {
      copyToast.value = false
    }, 2000)
  } catch {
    // Fallback
    const textarea = document.createElement('textarea')
    textarea.value = url
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    copyToast.value = true
    setTimeout(() => {
      copyToast.value = false
    }, 2000)
  }
}

function confirmDelete(image: ImageAsset) {
  deleteDialog.value = {
    open: true,
    loading: false,
    image,
  }
}

async function executeDelete() {
  if (!deleteDialog.value.image) return

  deleteDialog.value.loading = true
  try {
    await deleteImage(deleteDialog.value.image.id)
    await loadImages()
    deleteDialog.value.open = false
  } catch (e: any) {
    error.value = e.message
  } finally {
    deleteDialog.value.loading = false
  }
}

onMounted(loadImages)
</script>
