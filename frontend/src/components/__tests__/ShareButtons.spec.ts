import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ShareButtons from '@/components/ShareButtons.vue'

describe('ShareButtons', () => {
  beforeEach(() => {
    vi.stubGlobal('navigator', {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('renders three share buttons', () => {
    const wrapper = mount(ShareButtons, {
      props: {
        url: 'https://example.com/articles/test-article',
        title: 'Test Article',
        description: 'A test article description',
      },
    })

    const buttons = wrapper.findAll('button, a')
    expect(buttons.length).toBe(3)
  })

  it('Twitter link contains UTM params and article URL', () => {
    const wrapper = mount(ShareButtons, {
      props: {
        url: 'https://example.com/articles/test-article',
        title: 'Test Article',
        description: 'A test article description',
      },
    })

    const twitterLink = wrapper.find('a[aria-label="Share on X"]')
    expect(twitterLink.exists()).toBe(true)
    const href = twitterLink.attributes('href')!
    expect(href).toContain('twitter.com/intent/tweet')
    expect(decodeURIComponent(href)).toContain('utm_medium=twitter')
    expect(decodeURIComponent(href)).toContain('https://example.com/articles/test-article')
    expect(href).toContain(encodeURIComponent('Test Article'))
  })

  it('LinkedIn link contains UTM params and article URL', () => {
    const wrapper = mount(ShareButtons, {
      props: {
        url: 'https://example.com/articles/test-article',
        title: 'Test Article',
        description: 'A test article description',
      },
    })

    const linkedinLink = wrapper.find('a[aria-label="Share on LinkedIn"]')
    expect(linkedinLink.exists()).toBe(true)
    const href = linkedinLink.attributes('href')!
    expect(href).toContain('linkedin.com/sharing/share-offsite')
    expect(decodeURIComponent(href)).toContain('utm_medium=linkedin')
    expect(decodeURIComponent(href)).toContain('https://example.com/articles/test-article')
  })

  it('copy link button exists and uses button element', () => {
    const wrapper = mount(ShareButtons, {
      props: {
        url: 'https://example.com/articles/test-article',
        title: 'Test Article',
        description: 'A test article description',
      },
    })

    const copyButton = wrapper.find('button[aria-label="Copy link"]')
    expect(copyButton.exists()).toBe(true)
  })

  it('clicking copy button writes clean URL to clipboard', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined)
    vi.stubGlobal('navigator', { clipboard: { writeText } })

    const wrapper = mount(ShareButtons, {
      props: {
        url: 'https://example.com/articles/test-article',
        title: 'Test Article',
        description: 'A test article description',
      },
    })

    const copyButton = wrapper.find('button[aria-label="Copy link"]')
    await copyButton.trigger('click')

    expect(writeText).toHaveBeenCalledWith('https://example.com/articles/test-article')
    expect(writeText).toHaveBeenCalledTimes(1)

    vi.unstubAllGlobals()
  })

  it('shows toast notification after successful copy', async () => {
    vi.stubGlobal('navigator', {
      clipboard: { writeText: vi.fn().mockResolvedValue(undefined) },
    })

    const wrapper = mount(ShareButtons, {
      props: {
        url: 'https://example.com/articles/test-article',
        title: 'Test Article',
        description: 'A test article description',
      },
    })

    expect(wrapper.text()).not.toContain('Link copied to clipboard')

    const copyButton = wrapper.find('button[aria-label="Copy link"]')
    await copyButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Link copied to clipboard')

    vi.unstubAllGlobals()
  })
})
