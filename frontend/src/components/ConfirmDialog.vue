<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div
        v-if="state.visible"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm cursor-pointer"
        @click.self="onCancel"
      >
        <div class="rounded-xl border border-white/10 bg-surface-900 p-6 max-w-md w-full mx-4 shadow-2xl cursor-default">
          <div class="flex items-start gap-4 mb-4">
            <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" :class="iconBg">
              <svg class="w-5 h-5" :class="iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-display font-bold text-white">{{ state.title }}</h3>
              <p v-if="state.message" class="text-sm text-slate-400 mt-1">{{ state.message }}</p>
            </div>
          </div>
          <div class="flex items-center gap-3 justify-end">
            <button
              @click="onCancel"
              :disabled="state.loading"
              class="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ state.cancelText }}
            </button>
            <button
              @click="onConfirm"
              :disabled="state.loading"
              :class="confirmButtonClass"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="state.loading">Please wait...</span>
              <span v-else>{{ state.confirmText }}</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useConfirm } from '@/composables/useConfirm'

const { state, onConfirm, onCancel } = useConfirm()

const iconBg = computed(() => 'bg-accent-500/10')
const iconColor = computed(() => 'text-accent-400')

const confirmButtonClass = computed(() => {
  if (state.value.variant === 'danger') return 'bg-accent-600 hover:bg-accent-500 text-white'
  return 'bg-primary-600 hover:bg-primary-500 text-white'
})
</script>

<style scoped>
.dialog-enter-active,
.dialog-leave-active {
  transition: opacity 200ms ease;
}
.dialog-enter-active > div,
.dialog-leave-active > div {
  transition: transform 200ms ease, opacity 200ms ease;
}
.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
}
.dialog-enter-from > div {
  transform: scale(0.95);
  opacity: 0;
}
.dialog-leave-to > div {
  transform: scale(0.95);
  opacity: 0;
}
</style>
