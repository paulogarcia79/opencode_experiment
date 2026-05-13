<template>
  <div v-if="editor" class="rounded-xl border border-white/10 bg-white/[0.02] overflow-hidden">
    <!-- Toolbar -->
    <div class="border-b border-white/5 px-3 py-2.5 flex items-center gap-1 flex-wrap">
      <button
        type="button"
        @click="editor.chain().focus().toggleBold().run()"
        :class="[
          'p-2 rounded-lg text-sm font-bold transition-all duration-150 cursor-pointer',
          editor.isActive('bold') ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Bold"
      >
        B
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleItalic().run()"
        :class="[
          'p-2 rounded-lg text-sm italic transition-all duration-150 cursor-pointer',
          editor.isActive('italic') ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Italic"
      >
        I
      </button>
      <div class="w-px h-5 bg-white/10 mx-1" />
      <button
        type="button"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        :class="[
          'p-2 rounded-lg text-sm font-semibold transition-all duration-150 cursor-pointer',
          editor.isActive('heading', { level: 2 }) ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Heading 2"
      >
        H2
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        :class="[
          'p-2 rounded-lg text-sm font-semibold transition-all duration-150 cursor-pointer',
          editor.isActive('heading', { level: 3 }) ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Heading 3"
      >
        H3
      </button>
      <div class="w-px h-5 bg-white/10 mx-1" />
      <button
        type="button"
        @click="editor.chain().focus().toggleBulletList().run()"
        :class="[
          'p-2 rounded-lg text-sm transition-all duration-150 cursor-pointer',
          editor.isActive('bulletList') ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Bullet List"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleBlockquote().run()"
        :class="[
          'p-2 rounded-lg text-sm transition-all duration-150 cursor-pointer',
          editor.isActive('blockquote') ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Quote"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
        </svg>
      </button>
      <button
        type="button"
        @click="editor.chain().focus().toggleCodeBlock().run()"
        :class="[
          'p-2 rounded-lg text-sm font-mono transition-all duration-150 cursor-pointer',
          editor.isActive('codeBlock') ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Code Block"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
      </button>
      <div class="w-px h-5 bg-white/10 mx-1" />
      <button
        type="button"
        @click="triggerImageUpload"
        :class="[
          'p-2 rounded-lg text-sm transition-all duration-150 cursor-pointer',
          'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Upload Image"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </button>
      <input
        ref="imageInput"
        type="file"
        accept="image/*"
        class="hidden"
        @change="handleImageFileChange"
      />
      <button
        type="button"
        @click="setLink"
        :class="[
          'p-2 rounded-lg text-sm transition-all duration-150 cursor-pointer',
          editor.isActive('link') ? 'bg-primary-500/20 text-primary-400' : 'text-slate-400 hover:text-white hover:bg-white/5',
        ]"
        title="Link"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
        </svg>
      </button>
    </div>

    <!-- Editor Content -->
    <editor-content
      :editor="editor"
      class="prose prose-invert prose-slate max-w-none p-5 min-h-[350px] bg-transparent"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useEditor, EditorContent, type JSONContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Table from '@tiptap/extension-table'
import TableRow from '@tiptap/extension-table-row'
import TableCell from '@tiptap/extension-table-cell'
import TableHeader from '@tiptap/extension-table-header'
import { uploadImage } from '@/composables/useImageUpload'

const props = defineProps<{
  modelValue: JSONContent
  editable?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: JSONContent): void
}>()

const imageInput = ref<HTMLInputElement | null>(null)

const editor = useEditor({
  extensions: [
    StarterKit.configure({
      heading: {
        levels: [2, 3],
      },
    }),
    Link.configure({
      openOnClick: false,
    }),
    Image.configure({
      inline: true,
      allowBase64: false,
    }),
    Table.configure({
      resizable: true,
    }),
    TableRow,
    TableCell,
    TableHeader,
  ],
  content: props.modelValue,
  editable: props.editable !== false,
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getJSON())
  },
  editorProps: {
    handleDrop: (_view, event, _slice, moved) => {
      if (moved) return false
      const dt = event.dataTransfer
      if (!dt) return false
      const imageFile = getImageFileFromDataTransfer(dt)
      if (imageFile) {
        event.preventDefault()
        insertUploadedImage(imageFile)
        return true
      }
      return false
    },
    handlePaste: (_view, event, _slice) => {
      const dt = event.clipboardData
      if (!dt) return false
      const imageFile = getImageFileFromDataTransfer(dt)
      if (imageFile) {
        event.preventDefault()
        insertUploadedImage(imageFile)
        return true
      }
      return false
    },
  },
})

function setLink() {
  const url = window.prompt('Enter URL')
  if (url && editor.value) {
    editor.value.chain().focus().setLink({ href: url }).run()
  }
}

function triggerImageUpload() {
  imageInput.value?.click()
}

function handleImageFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    insertUploadedImage(file)
  }
  input.value = ''
}

function getImageFileFromDataTransfer(dataTransfer: DataTransfer): File | null {
  if (dataTransfer.files && dataTransfer.files.length > 0) {
    const file = dataTransfer.files[0]
    if (file.type.startsWith('image/')) {
      return file
    }
  }
  return null
}

async function insertUploadedImage(file: File) {
  if (!editor.value) return

  // Insert loading placeholder
  // Note: TipTap Image only preserves src, alt, title — use empty src as placeholder ID
  editor.value.chain().focus().setImage({ src: '', alt: 'Uploading...' }).run()

  try {
    const result = await uploadImage(file)

    // Replace placeholder with actual image
    editor.value.chain().focus().command(({ tr, dispatch }) => {
      if (!dispatch) return false

      const currentState = editor.value!.state
      let placeholderPos = -1
      currentState.doc.descendants((node, pos) => {
        if (node.type.name === 'image' && node.attrs.src === '') {
          placeholderPos = pos
          return false
        }
      })

      if (placeholderPos !== -1) {
        const imageNode = currentState.schema.nodes.image.create({
          src: result.url,
          alt: result.original_name,
          title: result.original_name,
        })
        tr.replaceWith(placeholderPos, placeholderPos + 1, imageNode)
        dispatch(tr)
        return true
      }
      return false
    }).run()
  } catch (error) {
    // Remove placeholder on error
    editor.value.chain().focus().command(({ tr, dispatch }) => {
      if (!dispatch) return false

      const currentState = editor.value!.state
      let placeholderPos = -1
      currentState.doc.descendants((node, pos) => {
        if (node.type.name === 'image' && node.attrs.src === '') {
          placeholderPos = pos
          return false
        }
      })

      if (placeholderPos !== -1) {
        tr.delete(placeholderPos, placeholderPos + 1)
        dispatch(tr)
        return true
      }
      return false
    }).run()

    console.error('Image upload failed:', error)
  }
}
</script>

<style>
/* Custom dark editor styles */
.ProseMirror {
  outline: none;
  color: #e2e8f0;
}
.ProseMirror p.is-editor-empty:first-child::before {
  color: #475569;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}
.ProseMirror pre {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 0.5rem !important;
  padding: 1rem !important;
}
.ProseMirror pre code {
  background: transparent !important;
  color: #a78bfa !important;
}
.ProseMirror blockquote {
  border-left-color: #7c3aed !important;
  background: rgba(124, 58, 237, 0.05) !important;
  padding: 0.75rem 1rem !important;
  border-radius: 0 0.5rem 0.5rem 0 !important;
}
.ProseMirror a {
  color: #a78bfa !important;
}

/* Image styles */
.ProseMirror img {
  max-width: 100%;
  height: auto;
  display: block;
  border-radius: 0.5rem;
}
.ProseMirror .ProseMirror-selectednode img {
  outline: 2px solid #a78bfa;
  outline-offset: 2px;
}

/* Table styles */
.ProseMirror table {
  border-collapse: collapse;
  margin: 1rem 0;
  width: 100%;
}
.ProseMirror td,
.ProseMirror th {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 0.75rem;
  min-width: 100px;
}
.ProseMirror th {
  background: rgba(124, 58, 237, 0.1);
  font-weight: 600;
}
.ProseMirror td {
  background: rgba(255, 255, 255, 0.02);
}
.ProseMirror .selectedCell:after {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(124, 58, 237, 0.15);
  pointer-events: none;
}
</style>
