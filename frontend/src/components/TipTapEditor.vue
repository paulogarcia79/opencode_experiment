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
    <editor-content :editor="editor" class="prose prose-invert prose-slate max-w-none p-5 min-h-[350px] bg-transparent" />
  </div>
</template>

<script setup lang="ts">
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'

const props = defineProps<{
  modelValue: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: any): void
}>()

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
  ],
  content: props.modelValue,
  onUpdate: ({ editor }) => {
    emit('update:modelValue', editor.getJSON())
  },
})

function setLink() {
  const url = window.prompt('Enter URL')
  if (url && editor.value) {
    editor.value.chain().focus().setLink({ href: url }).run()
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
</style>
