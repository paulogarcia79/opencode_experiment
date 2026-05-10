import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import TagInput from '@/components/TagInput.vue'

vi.mock('@/composables/useTagSearch', () => ({
  useTagSearch: () => {
    const suggestions = ref([
      { name: 'docker', slug: 'docker' },
      { name: 'devops', slug: 'devops' },
    ])
    return {
      suggestions,
      fetchSuggestions: vi.fn(),
    }
  },
}))

describe('TagInput', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('shows matching tag suggestions when typing', async () => {
    const wrapper = mount(TagInput, {
      props: { modelValue: [] },
    })

    const input = wrapper.find('input')
    await input.setValue('d')
    await vi.advanceTimersByTime(150)
    await flushPromises()

    expect(wrapper.text()).toContain('docker')
    expect(wrapper.text()).toContain('devops')
  })

  it('creates a new tag on Enter', async () => {
    const wrapper = mount(TagInput, {
      props: { modelValue: [] },
    })

    const input = wrapper.find('input')
    await input.setValue('newtag')
    await input.trigger('keydown.enter')

    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)
    const emitted = wrapper.emitted('update:modelValue')![0] as any
    expect(emitted[0]).toEqual([{ name: 'newtag', slug: 'newtag' }])
  })

  it('disables input when max 8 tags reached', () => {
    const tags = Array.from({ length: 8 }, (_, i) => ({ name: `tag${i}`, slug: `tag${i}` }))
    const wrapper = mount(TagInput, {
      props: { modelValue: tags },
    })

    expect(wrapper.find('input').exists()).toBe(false)
  })

  it('removes last tag on backspace when input is empty', async () => {
    const wrapper = mount(TagInput, {
      props: { modelValue: [{ name: 'docker', slug: 'docker' }] },
    })

    const input = wrapper.find('input')
    await input.setValue('')
    await input.trigger('keydown.backspace')

    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)
    const emitted = wrapper.emitted('update:modelValue')![0] as any
    expect(emitted[0]).toEqual([])
  })

  it('removes tag when clicking x', async () => {
    const wrapper = mount(TagInput, {
      props: { modelValue: [{ name: 'docker', slug: 'docker' }, { name: 'vue', slug: 'vue' }] },
    })

    const removeButtons = wrapper.findAll('button[type="button"]')
    await removeButtons[0].trigger('click')

    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)
    const emitted = wrapper.emitted('update:modelValue')![0] as any
    expect(emitted[0]).toEqual([{ name: 'vue', slug: 'vue' }])
  })
})
