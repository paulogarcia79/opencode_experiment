import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import TipTapRenderer from '@/components/TipTapRenderer.vue'

vi.mock('@/composables/useTipTap', () => ({
  renderTipTapJSON: vi.fn(),
}))

import { renderTipTapJSON } from '@/composables/useTipTap'

describe('TipTapRenderer', () => {
  it('renders TipTap JSON to HTML', () => {
    vi.mocked(renderTipTapJSON).mockReturnValue('<p>Hello world</p>')

    const wrapper = mount(TipTapRenderer, {
      props: { content: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Hello world' }] }] } },
    })

    expect(wrapper.find('.prose').exists()).toBe(true)
    expect(wrapper.html()).toContain('<p>Hello world</p>')
  })

  it('renders empty content gracefully', () => {
    vi.mocked(renderTipTapJSON).mockReturnValue('')

    const wrapper = mount(TipTapRenderer, {
      props: { content: { type: 'doc', content: [] } },
    })

    expect(wrapper.find('.prose').exists()).toBe(true)
  })

  it('handles null content gracefully', () => {
    vi.mocked(renderTipTapJSON).mockReturnValue('')

    const wrapper = mount(TipTapRenderer, {
      props: { content: null as any },
    })

    expect(wrapper.find('.prose').exists()).toBe(true)
  })

  it('handles undefined content gracefully', () => {
    vi.mocked(renderTipTapJSON).mockReturnValue('')

    const wrapper = mount(TipTapRenderer, {
      props: { content: undefined as any },
    })

    expect(wrapper.find('.prose').exists()).toBe(true)
  })
})
