/**
 * Lightweight composable for managing document <head> meta tags.
 * Updates title, description, canonical, OpenGraph, and Twitter Card meta tags.
 */
export interface HeadMeta {
  title?: string
  description?: string
  canonical?: string
  ogTitle?: string
  ogDescription?: string
  ogType?: string
  ogUrl?: string
  twitterCard?: string
  twitterTitle?: string
  twitterDescription?: string
}

const SITE_NAME = 'Tech & Games Blog'
const DEFAULT_DESCRIPTION = 'Deep dives into software development, game design, and the technology shaping our digital world.'

function setMetaTag(name: string, content: string, property = false) {
  const attr = property ? 'property' : 'name'
  let el = document.querySelector(`meta[${attr}="${name}"]`) as HTMLMetaElement | null
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, name)
    document.head.appendChild(el)
  }
  el.content = content
}

function setLinkTag(rel: string, href: string) {
  let el = document.querySelector(`link[rel="${rel}"]`) as HTMLLinkElement | null
  if (!el) {
    el = document.createElement('link')
    el.rel = rel
    document.head.appendChild(el)
  }
  el.href = href
}

export function useHead(meta: HeadMeta) {
  const title = meta.title ? `${meta.title} | ${SITE_NAME}` : SITE_NAME
  document.title = title

  const description = meta.description || DEFAULT_DESCRIPTION
  setMetaTag('description', description)

  // OpenGraph
  if (meta.ogTitle || meta.title) {
    setMetaTag('og:title', meta.ogTitle || meta.title || SITE_NAME, true)
  }
  if (meta.ogDescription || meta.description) {
    setMetaTag('og:description', meta.ogDescription || meta.description || DEFAULT_DESCRIPTION, true)
  }
  setMetaTag('og:type', meta.ogType || 'website', true)
  if (meta.ogUrl) {
    setMetaTag('og:url', meta.ogUrl, true)
  }
  setMetaTag('og:site_name', SITE_NAME, true)

  // Twitter Cards
  setMetaTag('twitter:card', meta.twitterCard || 'summary')
  if (meta.twitterTitle || meta.title) {
    setMetaTag('twitter:title', meta.twitterTitle || meta.title || SITE_NAME)
  }
  if (meta.twitterDescription || meta.description) {
    setMetaTag('twitter:description', meta.twitterDescription || meta.description || DEFAULT_DESCRIPTION)
  }

  // Canonical
  if (meta.canonical) {
    setLinkTag('canonical', meta.canonical)
  }
}

/**
 * Reset meta tags to default site values.
 */
export function resetHead() {
  document.title = SITE_NAME
  setMetaTag('description', DEFAULT_DESCRIPTION)
  setMetaTag('og:title', SITE_NAME, true)
  setMetaTag('og:description', DEFAULT_DESCRIPTION, true)
  setMetaTag('og:type', 'website', true)
  setMetaTag('og:site_name', SITE_NAME, true)
  setMetaTag('twitter:card', 'summary')
  setMetaTag('twitter:title', SITE_NAME)
  setMetaTag('twitter:description', DEFAULT_DESCRIPTION)
}
