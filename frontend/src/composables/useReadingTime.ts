/**
 * Recursively extract plain text from a TipTap JSON document.
 */
function extractTextFromTipTap(content: any): string {
  const texts: string[] = []

  function walk(node: any) {
    if (!node) return
    if (typeof node === 'object') {
      if (node.type === 'text' && typeof node.text === 'string') {
        texts.push(node.text)
      }
      if (Array.isArray(node.content)) {
        node.content.forEach(walk)
      }
    }
  }

  walk(content)
  return texts.join(' ')
}

/**
 * Estimate reading time in minutes from TipTap JSON content.
 * Average reading speed: 200 words per minute.
 */
export function estimateReadingTime(content: any): number {
  const text = extractTextFromTipTap(content).trim()
  if (!text) return 0
  const wordCount = text.split(/\s+/).length
  const minutes = Math.ceil(wordCount / 200)
  return minutes
}

/**
 * Format reading time as a human-readable string.
 */
export function formatReadingTime(minutes: number): string {
  if (minutes <= 1) return '1 min read'
  return `${minutes} min read`
}
