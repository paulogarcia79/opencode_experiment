import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import { generateHTML } from '@tiptap/html'
import type { JSONContent } from '@tiptap/vue-3'

export function renderTipTapJSON(json: JSONContent | null): string {
  if (!json) return ''
  return generateHTML(json, [
    StarterKit,
    Link,
    Image,
    Table,
    TableRow,
    TableCell,
    TableHeader,
  ])
}
