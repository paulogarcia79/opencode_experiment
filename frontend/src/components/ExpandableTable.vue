<template>
  <div class="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden">
    <table class="w-full text-sm">
      <thead class="border-b border-white/5">
        <tr>
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider whitespace-nowrap"
            :class="{ 'cursor-pointer hover:text-white select-none': col.sortable }"
            @click="col.sortable && $emit('sort', col.key)"
          >
            <span class="inline-flex items-center gap-1">
              {{ col.label }}
              <svg
                v-if="col.sortable && sortColumn === col.key"
                class="w-3 h-3 transition-transform duration-200"
                :class="{ 'rotate-180': sortOrder === 'desc' }"
                fill="none" viewBox="0 0 24 24" stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
              </svg>
            </span>
          </th>
          <th v-if="$slots['row-actions']" class="px-5 py-4 text-right font-medium text-slate-500 text-xs uppercase tracking-wider">
            Actions
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-white/5">
        <template v-for="row in rows" :key="row.id">
          <tr
            class="hover:bg-white/[0.02] transition-colors duration-150 cursor-pointer"
            @click="toggleRow(row.id)"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              class="px-5 py-4"
            >
              <slot :name="'cell-' + col.key" :row="row" :column="col">
                {{ row[col.key] }}
              </slot>
            </td>
            <td v-if="$slots['row-actions']" class="px-5 py-4 text-right">
              <slot name="row-actions" :row="row" />
            </td>
          </tr>
          <tr v-if="isExpanded(row.id)" class="bg-white/[0.03]">
            <td :colspan="columns.length + ($slots['row-actions'] ? 1 : 0)" class="px-5 py-4">
              <slot name="expanded-row" :row="row" />
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <div v-if="rows.length === 0" class="px-6 py-16 text-center">
      <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
        <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <p class="text-slate-500 font-mono text-sm">No items to display.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface TableColumn {
  key: string
  label: string
  sortable?: boolean
}

export interface TableRow {
  id: string
  [key: string]: unknown
}

const props = withDefaults(defineProps<{
  columns: TableColumn[]
  rows: any[]
  expandedIds?: string[]
  sortColumn?: string
  sortOrder?: string
}>(), {
  expandedIds: () => [],
  sortColumn: '',
  sortOrder: 'desc',
})

const emit = defineEmits<{
  expand: [id: string]
  collapse: [id: string]
  sort: [column: string]
}>()

function isExpanded(id: string): boolean {
  return props.expandedIds.includes(id)
}

function toggleRow(id: string) {
  if (isExpanded(id)) {
    emit('collapse', id)
  } else {
    emit('expand', id)
  }
}
</script>
