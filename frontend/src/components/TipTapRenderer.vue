<template>
  <article class="prose prose-invert prose-slate max-w-none">
    <div v-html="htmlContent" />
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { renderTipTapJSON } from '@/composables/useTipTap'

const props = defineProps<{
  content: any
}>()

const htmlContent = computed(() => renderTipTapJSON(props.content))
</script>

<style scoped>
.prose-invert :deep(pre) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
}
.prose-invert :deep(pre code) {
  background: transparent;
  color: #a78bfa;
}
.prose-invert :deep(blockquote) {
  border-left-color: #7c3aed;
  background: rgba(124, 58, 237, 0.05);
  border-radius: 0 0.5rem 0.5rem 0;
  padding: 1rem 1.25rem;
}
.prose-invert :deep(a) {
  color: #a78bfa;
  text-decoration: none;
}
.prose-invert :deep(a:hover) {
  text-decoration: underline;
}
.prose-invert :deep(strong) {
  color: #f8fafc;
}
.prose-invert :deep(h2),
.prose-invert :deep(h3) {
  color: #f8fafc;
}
.prose-invert :deep(hr) {
  border-color: rgba(255, 255, 255, 0.1);
}
.prose-invert :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.75rem;
  margin: 1.5rem 0;
}
.prose-invert :deep(table) {
  border-collapse: collapse;
  margin: 1.5rem 0;
  width: 100%;
}
.prose-invert :deep(td),
.prose-invert :deep(th) {
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0.5rem 0.75rem;
  min-width: 100px;
}
.prose-invert :deep(th) {
  background: rgba(124, 58, 237, 0.1);
  font-weight: 600;
}
.prose-invert :deep(td) {
  background: rgba(255, 255, 255, 0.02);
}
</style>
