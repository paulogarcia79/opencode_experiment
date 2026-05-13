import { ref } from 'vue'

export interface ConfirmState {
  visible: boolean
  title: string
  message: string
  confirmText: string
  cancelText: string
  variant: 'danger' | 'warning' | 'default'
  loading: boolean
}

const state = ref<ConfirmState>({
  visible: false,
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  variant: 'default',
  loading: false,
})

let resolvePromise: ((value: boolean) => void) | null = null

export function useConfirm() {
  function confirm(title: string, message?: string, variant: 'danger' | 'warning' | 'default' = 'default'): Promise<boolean> {
    state.value = {
      visible: true,
      title,
      message: message || '',
      confirmText: 'Confirm',
      cancelText: 'Cancel',
      variant,
      loading: false,
    }
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }

  function onConfirm() {
    resolvePromise?.(true)
    state.value.visible = false
    resolvePromise = null
  }

  function onCancel() {
    resolvePromise?.(false)
    state.value.visible = false
    resolvePromise = null
  }

  return { state, confirm, onConfirm, onCancel }
}
