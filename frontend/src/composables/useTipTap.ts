import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import { generateHTML } from '@tiptap/html'

export function renderTipTapJSON(json: any): string {
  if (!json) return ''
  return generateHTML(json, [StarterKit, Link, Image])
}
