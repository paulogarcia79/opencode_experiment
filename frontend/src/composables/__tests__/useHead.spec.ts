import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { useHead, resetHead } from '@/composables/useHead'

describe('useHead', () => {
  beforeEach(() => {
    // Clean up any meta tags added by previous tests
    document.title = ''
    const metas = document.querySelectorAll('meta[name^="description"], meta[name^="twitter"], meta[property^="og"]')
    metas.forEach((el) => el.remove())
    const links = document.querySelectorAll('link[rel="canonical"]')
    links.forEach((el) => el.remove())
    const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]')
    jsonLdScripts.forEach((el) => el.remove())
  })

  afterEach(() => {
    resetHead()
  })

  it('sets document title with site name suffix', () => {
    useHead({ title: 'My Article' })
    expect(document.title).toBe('My Article | Tech & Games Blog')
  })

  it('sets default title when no title provided', () => {
    useHead({})
    expect(document.title).toBe('Tech & Games Blog')
  })

  it('sets description meta tag', () => {
    useHead({ description: 'A great article' })
    const meta = document.querySelector('meta[name="description"]') as HTMLMetaElement
    expect(meta).not.toBeNull()
    expect(meta.content).toBe('A great article')
  })

  it('sets OpenGraph tags', () => {
    useHead({
      title: 'Test',
      ogTitle: 'OG Test',
      ogDescription: 'OG Description',
      ogType: 'article',
      ogUrl: 'https://example.com/test',
    })

    expect(document.querySelector('meta[property="og:title"]')?.getAttribute('content')).toBe('OG Test')
    expect(document.querySelector('meta[property="og:description"]')?.getAttribute('content')).toBe('OG Description')
    expect(document.querySelector('meta[property="og:type"]')?.getAttribute('content')).toBe('article')
    expect(document.querySelector('meta[property="og:url"]')?.getAttribute('content')).toBe('https://example.com/test')
    expect(document.querySelector('meta[property="og:site_name"]')?.getAttribute('content')).toBe('Tech & Games Blog')
  })

  it('sets Twitter Card tags', () => {
    useHead({
      title: 'Test',
      twitterCard: 'summary_large_image',
      twitterTitle: 'Twitter Test',
      twitterDescription: 'Twitter Description',
    })

    expect(document.querySelector('meta[name="twitter:card"]')?.getAttribute('content')).toBe('summary_large_image')
    expect(document.querySelector('meta[name="twitter:title"]')?.getAttribute('content')).toBe('Twitter Test')
    expect(document.querySelector('meta[name="twitter:description"]')?.getAttribute('content')).toBe('Twitter Description')
  })

  it('sets canonical link', () => {
    useHead({ canonical: 'https://example.com/canonical' })
    const link = document.querySelector('link[rel="canonical"]') as HTMLLinkElement
    expect(link).not.toBeNull()
    expect(link.href).toBe('https://example.com/canonical')
  })

  it('resets to defaults', () => {
    useHead({ title: 'Custom', description: 'Custom desc' })
    resetHead()
    expect(document.title).toBe('Tech & Games Blog')
    expect(document.querySelector('meta[name="description"]')?.getAttribute('content')).toBe(
      'Deep dives into software development, game design, and the technology shaping our digital world.'
    )
  })

  it('injects JSON-LD script tag', () => {
    useHead({
      jsonLd: {
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: 'Test Article',
      },
    })

    const script = document.querySelector('script[type="application/ld+json"]')
    expect(script).not.toBeNull()
    const data = JSON.parse(script!.textContent!)
    expect(data['@context']).toBe('https://schema.org')
    expect(data['@type']).toBe('Article')
    expect(data.headline).toBe('Test Article')
  })

  it('updates existing JSON-LD script tag instead of creating duplicate', () => {
    useHead({
      jsonLd: { '@context': 'https://schema.org', '@type': 'Article', headline: 'First' },
    })
    useHead({
      jsonLd: { '@context': 'https://schema.org', '@type': 'Article', headline: 'Second' },
    })

    const scripts = document.querySelectorAll('script[type="application/ld+json"]')
    expect(scripts.length).toBe(1)
    const data = JSON.parse(scripts[0].textContent!)
    expect(data.headline).toBe('Second')
  })

  it('resetHead removes JSON-LD script tag', () => {
    useHead({
      jsonLd: { '@context': 'https://schema.org', '@type': 'Article', headline: 'Test' },
    })
    expect(document.querySelector('script[type="application/ld+json"]')).not.toBeNull()

    resetHead()
    expect(document.querySelector('script[type="application/ld+json"]')).toBeNull()
  })
})
