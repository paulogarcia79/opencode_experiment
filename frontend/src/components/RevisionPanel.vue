<template>
  <Teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/50" @click="close" />
      <div class="absolute right-0 top-0 bottom-0 w-full max-w-xl bg-[#1a1a2e] border-l border-white/10 flex flex-col shadow-2xl">
        <!-- Header -->
        <div class="flex items-center justify-between px-6 py-4 border-b border-white/10">
          <h2 class="text-lg font-display font-bold text-white">Revision History</h2>
          <button @click="close" class="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors cursor-pointer">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="flex-1 flex items-center justify-center">
          <div class="animate-spin h-8 w-8 border-2 border-primary-600 border-t-transparent rounded-full" />
        </div>

        <!-- Error -->
        <div v-else-if="error" class="flex-1 flex items-center justify-center px-6">
          <p class="text-red-400">{{ error }}</p>
        </div>

        <!-- Empty -->
        <div v-else-if="revisions.length === 0" class="flex-1 flex items-center justify-center px-6">
          <p class="text-slate-500">No revisions yet</p>
        </div>

        <!-- Content -->
        <div v-else class="flex-1 flex flex-col min-h-0">
          <!-- Revision list -->
          <div class="px-6 py-4 border-b border-white/10 max-h-64 overflow-y-auto">
            <ul class="space-y-2">
              <li v-for="rev in revisions" :key="rev.version_number">
                <button
                  @click="selectRevision(rev.version_number)"
                  class="w-full text-left px-4 py-3 rounded-lg transition-colors cursor-pointer"
                  :class="selectedVersion === rev.version_number ? 'bg-primary-600/20 border border-primary-500/30' : 'bg-white/5 hover:bg-white/10 border border-transparent'"
                >
                  <div class="flex items-center gap-3">
                    <span class="text-xs font-mono text-primary-400 font-bold">v{{ rev.version_number }}</span>
                    <span
                      class="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full font-medium"
                      :class="{
                        'bg-emerald-500/20 text-emerald-400': rev.change_type === 'publish',
                        'bg-slate-500/20 text-slate-400': rev.change_type === 'save',
                        'bg-amber-500/20 text-amber-400': rev.change_type === 'restore',
                      }"
                    >
                      {{ rev.change_type }}
                    </span>
                    <span class="text-sm text-white truncate flex-1">{{ rev.title }}</span>
                  </div>
                  <div class="text-xs text-slate-500 mt-1">{{ formatDate(rev.created_at) }}</div>
                </button>
              </li>
            </ul>
          </div>

          <!-- Diff view -->
          <div v-if="selectedRevision" class="flex-1 overflow-y-auto px-6 py-4 space-y-6">
            <div v-if="diffs.title" class="space-y-1">
              <h3 class="text-sm font-medium text-slate-400">Title</h3>
              <div class="px-4 py-3 rounded-lg bg-white/5 text-sm font-display">
                <span v-for="(part, i) in diffs.title" :key="i" :class="diffClass(part)">
                  {{ part.value }}
                </span>
              </div>
            </div>

            <div v-if="diffs.description" class="space-y-1">
              <h3 class="text-sm font-medium text-slate-400">Description</h3>
              <div class="px-4 py-3 rounded-lg bg-white/5 text-sm">
                <span v-for="(part, i) in diffs.description" :key="i" :class="diffClass(part)">
                  {{ part.value }}
                </span>
              </div>
            </div>

            <div v-if="diffs.content" class="space-y-1">
              <h3 class="text-sm font-medium text-slate-400">Content</h3>
              <div class="px-4 py-3 rounded-lg bg-white/5 text-sm leading-relaxed whitespace-pre-wrap">
                <span v-for="(part, i) in diffs.content" :key="i" :class="diffClass(part)">
                  {{ part.value }}
                </span>
              </div>
            </div>

            <div v-if="diffs.tags" class="space-y-1">
              <h3 class="text-sm font-medium text-slate-400">Tags</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in diffs.tags"
                  :key="tag.value"
                  class="text-xs px-2 py-1 rounded-full font-medium"
                  :class="{
                    'bg-emerald-500/20 text-emerald-400': tag.added,
                    'bg-red-500/20 text-red-400 line-through': tag.removed,
                    'bg-slate-500/20 text-slate-400': !tag.added && !tag.removed,
                  }"
                >
                  {{ tag.value }}
                </span>
              </div>
            </div>

            <!-- Restore button -->
            <button
              @click="confirmRestore"
              class="w-full py-3 px-4 bg-accent-600 hover:bg-accent-500 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer shadow-lg shadow-accent-600/20"
            >
              Restore this version
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Confirmation dialog -->
  <Teleport to="body">
    <div v-if="showConfirm" class="fixed inset-0 z-[60] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-black/60" @click="showConfirm = false" />
      <div class="relative bg-[#1a1a2e] border border-white/10 rounded-xl p-6 max-w-md w-full shadow-2xl">
        <h3 class="text-lg font-display font-bold text-white mb-2">Restore Revision</h3>
        <p class="text-sm text-slate-400 mb-6">
          Restore article to version {{ selectedVersion }}? This will overwrite your current draft.
        </p>
        <div class="flex gap-3 justify-end">
          <button
            @click="showConfirm = false"
            class="px-4 py-2 border border-white/10 text-sm font-medium text-slate-400 rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            @click="executeRestore"
            :disabled="restoring"
            class="px-4 py-2 bg-accent-600 hover:bg-accent-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors cursor-pointer"
          >
            <span v-if="restoring">Restoring...</span>
            <span v-else>Restore</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, toRef } from 'vue'
import { diffChars, diffWords } from 'diff'
import { extractPlainText } from '@/composables/extractPlainText'
import { useRevisions } from '@/composables/useRevisions'

interface DiffPart {
  value: string
  added?: boolean
  removed?: boolean
}

interface TagDiff {
  value: string
  added: boolean
  removed: boolean
}

interface Diffs {
  title?: DiffPart[]
  description?: DiffPart[]
  content?: DiffPart[]
  tags?: TagDiff[]
}

const props = defineProps<{
  isOpen: boolean
  articleId: string
  currentArticle: {
    title: string
    description: string
    content: Record<string, unknown>
    tags: { name: string }[]
  }
}>()

const emit = defineEmits<{
  close: []
  restored: [article: unknown]
}>()

const showConfirm = ref(false)
const restoring = ref(false)

const { revisions, currentRevision, loading, error, fetchList, fetch, restore } = useRevisions(toRef(props, 'articleId'))

const selectedVersion = ref<number | null>(null)

const selectedRevision = computed(() => currentRevision.value)

watch(() => props.isOpen, (open) => {
  if (open) {
    fetchList()
    selectedVersion.value = null
    currentRevision.value = null
  }
})

async function selectRevision(versionNumber: number) {
  selectedVersion.value = versionNumber
  await fetch(versionNumber)
}

const diffs = computed<Diffs>(() => {
  if (!selectedRevision.value) return {}

  const rev = selectedRevision.value
  const current = props.currentArticle
  const result: Diffs = {}

  const titleDiff = diffChars(rev.title, current.title)
  if (titleDiff.some(p => p.added || p.removed)) {
    result.title = titleDiff as DiffPart[]
  }

  const revDesc = rev.description || ''
  const curDesc = current.description || ''
  const descDiff = diffChars(revDesc, curDesc)
  if (descDiff.some(p => p.added || p.removed)) {
    result.description = descDiff as DiffPart[]
  }

  const revText = extractPlainText(rev.content)
  const curText = extractPlainText(current.content)
  const contentDiff = diffWords(revText, curText)
  if (contentDiff.some(p => p.added || p.removed)) {
    result.content = contentDiff as DiffPart[]
  }

  const revTags = new Set(rev.tag_names)
  const curTags = new Set(current.tags.map(t => t.name))
  const allTags = [...new Set([...revTags, ...curTags])]
  const tagDiffs: TagDiff[] = allTags.map(tag => ({
    value: tag,
    added: !revTags.has(tag),
    removed: !curTags.has(tag),
  }))
  if (tagDiffs.some(t => t.added || t.removed)) {
    result.tags = tagDiffs
  }

  return result
})

function diffClass(part: DiffPart) {
  if (part.added) return 'bg-emerald-500/20 text-emerald-400'
  if (part.removed) return 'bg-red-500/20 text-red-400 line-through'
  return 'text-slate-300'
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function close() {
  emit('close')
}

function confirmRestore() {
  showConfirm.value = true
}

async function executeRestore() {
  if (!selectedVersion.value) return
  restoring.value = true
  try {
    const result = await restore(selectedVersion.value)
    showConfirm.value = false
    emit('restored', result)
  } catch {
    showConfirm.value = false
  } finally {
    restoring.value = false
  }
}
</script>
