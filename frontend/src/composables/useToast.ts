import { ref } from 'vue'

export interface Toast {
  id: number
  message: string
  variant: 'error' | 'success' | 'info'
}

const toasts = ref<Toast[]>([])
let nextId = 0

export function useToast() {
  function show(message: string, variant: 'error' | 'success' | 'info' = 'error') {
    const id = nextId++
    toasts.value.push({ id, message, variant })
    setTimeout(() => {
      toasts.value = toasts.value.filter((t) => t.id !== id)
    }, 5000)
  }

  function remove(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, show, remove }
}
