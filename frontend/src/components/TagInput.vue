<template>
  <div class="relative">
    <div
      class="flex flex-wrap gap-2 items-center w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2"
      :class="{ 'opacity-50': disabled }"
    >
      <span
        v-for="(tag, index) in modelValue"
        :key="tag.slug"
        class="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-primary-500/20 text-primary-300 text-xs font-mono"
      >
        {{ tag.name }}
        <button
          v-if="!disabled"
          type="button"
          class="text-primary-400 hover:text-white"
          @click="removeTag(index)"
        >
          <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
      <input
        v-if="!disabled"
        v-model="query"
        type="text"
        class="flex-1 min-w-[80px] bg-transparent text-white text-sm placeholder-slate-500 focus:outline-none"
        placeholder="Add tag..."
        @keydown.enter.prevent="handleEnter"
        @keydown.backspace="handleBackspace"
      />
    </div>

    <!-- Suggestions dropdown -->
    <div
      v-if="showSuggestions && filteredSuggestions.length > 0"
      class="absolute z-50 w-full mt-1 bg-surface-900 border border-white/10 rounded-lg shadow-xl overflow-hidden"
    >
      <button
        v-for="suggestion in filteredSuggestions"
        :key="suggestion.slug"
        type="button"
        class="w-full text-left px-3 py-2 text-sm text-slate-300 hover:bg-white/5 transition-colors"
        @click="selectTag(suggestion)"
      >
        {{ suggestion.name }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useTagSearch } from '@/composables/useTagSearch'

export interface TagItem {
  name: string
  slug: string
}

const props = defineProps<{
  modelValue: TagItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: TagItem[]]
}>()

const query = ref('')
const showSuggestions = ref(false)
const { suggestions, fetchSuggestions } = useTagSearch()

const disabled = computed(() => props.modelValue.length >= 8)

const filteredSuggestions = computed(() => {
  const q = query.value.toLowerCase()
  return suggestions.value.filter(
    (s) =>
      s.name.toLowerCase().includes(q) &&
      !props.modelValue.some((t) => t.slug === s.slug)
  )
})

let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(query, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSuggestions(val)
    showSuggestions.value = true
  }, 150)
})

function selectTag(tag: TagItem) {
  if (props.modelValue.length >= 8) return
  emit('update:modelValue', [...props.modelValue, tag])
  query.value = ''
  showSuggestions.value = false
}

function handleEnter() {
  const name = query.value.trim()
  if (!name) return
  if (props.modelValue.length >= 8) return
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
  if (!slug) return
  if (props.modelValue.some((t) => t.slug === slug)) {
    query.value = ''
    return
  }
  emit('update:modelValue', [...props.modelValue, { name, slug }])
  query.value = ''
  showSuggestions.value = false
}

function handleBackspace() {
  if (query.value === '' && props.modelValue.length > 0) {
    emit('update:modelValue', props.modelValue.slice(0, -1))
  }
}

function removeTag(index: number) {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== index))
}
</script>
