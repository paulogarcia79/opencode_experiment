<template>
  <div class="flex items-center gap-3">
    <a
      :href="twitterUrl"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Share on X"
      class="p-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all duration-200"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
      </svg>
    </a>
    <a
      :href="linkedinUrl"
      target="_blank"
      rel="noopener noreferrer"
      aria-label="Share on LinkedIn"
      class="p-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all duration-200"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
      </svg>
    </a>
    <button
      @click="copyLink"
      aria-label="Copy link"
      class="p-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all duration-200 cursor-pointer"
    >
      <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    </button>
  </div>

  <!-- Copy Toast -->
  <div
    v-if="copyToast"
    class="fixed bottom-6 right-6 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium flex items-center gap-2 transition-all duration-300"
  >
    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
    </svg>
    Link copied to clipboard
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  url: string
  title: string
  description?: string
}>()

const copyToast = ref(false)

const twitterUrl = computed(() => {
  const text = encodeURIComponent(props.title)
  const shareUrl = `${props.url}?utm_source=share&utm_medium=twitter&utm_campaign=social`
  return `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${text}`
})

const linkedinUrl = computed(() => {
  const shareUrl = `${props.url}?utm_source=share&utm_medium=linkedin&utm_campaign=social`
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`
})

async function copyLink() {
  try {
    await navigator.clipboard.writeText(props.url)
    copyToast.value = true
    setTimeout(() => {
      copyToast.value = false
    }, 2000)
  } catch {
    // Fallback for browsers without clipboard API
    const textarea = document.createElement('textarea')
    textarea.value = props.url
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
</script>
