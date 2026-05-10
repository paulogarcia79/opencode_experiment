import { describe, it, expect } from 'vitest'
import { estimateReadingTime, formatReadingTime } from '@/composables/useReadingTime'

describe('useReadingTime', () => {
  describe('estimateReadingTime', () => {
    it('returns 0 for empty content', () => {
      expect(estimateReadingTime(null)).toBe(0)
      expect(estimateReadingTime({})).toBe(0)
      expect(estimateReadingTime({ content: [] })).toBe(0)
    })

    it('estimates 1 minute for a short text', () => {
      const content = {
        type: 'doc',
        content: [
          { type: 'paragraph', content: [{ type: 'text', text: 'Hello world' }] },
        ],
      }
      expect(estimateReadingTime(content)).toBe(1)
    })

    it('estimates correctly for 400 words', () => {
      const words = Array(400).fill('word').join(' ')
      const content = {
        type: 'doc',
        content: [
          { type: 'paragraph', content: [{ type: 'text', text: words }] },
        ],
      }
      expect(estimateReadingTime(content)).toBe(2)
    })

    it('recursively counts text across nested nodes', () => {
      const content = {
        type: 'doc',
        content: [
          {
            type: 'bulletList',
            content: [
              {
                type: 'listItem',
                content: [
                  { type: 'paragraph', content: [{ type: 'text', text: 'First item' }] },
                ],
              },
              {
                type: 'listItem',
                content: [
                  { type: 'paragraph', content: [{ type: 'text', text: 'Second item' }] },
                ],
              },
            ],
          },
        ],
      }
      expect(estimateReadingTime(content)).toBe(1)
    })
  })

  describe('formatReadingTime', () => {
    it('formats 1 minute', () => {
      expect(formatReadingTime(1)).toBe('1 min read')
    })

    it('formats multiple minutes', () => {
      expect(formatReadingTime(5)).toBe('5 min read')
    })

    it('formats 0 as 1 min read', () => {
      expect(formatReadingTime(0)).toBe('1 min read')
    })
  })
})
