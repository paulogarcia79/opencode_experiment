import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ExpandableTable from '@/components/ExpandableTable.vue'

describe('ExpandableTable', () => {
  const columns = [
    { key: 'title', label: 'Title' },
    { key: 'author', label: 'Author' },
    { key: 'status', label: 'Status' },
  ]

  const rows = [
    { id: '1', title: 'Article One', author: 'Alice', status: 'published' },
    { id: '2', title: 'Article Two', author: 'Bob', status: 'draft' },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  function mountTable(props = {}) {
    return mount(ExpandableTable as any, {
      props: {
        columns,
        rows,
        ...props,
      },
      slots: {
        'expanded-row': `<template #expanded-row="{ row }"><div class="detail-card">{{ row.title }} details</div></template>`,
      },
    })
  }

  it('renders column headers', () => {
    const wrapper = mountTable()
    const headers = wrapper.findAll('th')
    expect(headers.length).toBe(columns.length)
    expect(headers[0].text()).toContain('Title')
    expect(headers[1].text()).toContain('Author')
    expect(headers[2].text()).toContain('Status')
  })

  it('renders all rows', () => {
    const wrapper = mountTable()
    const bodyRows = wrapper.findAll('tbody tr').filter(r => !r.attributes('class')?.includes('expanded'))
    expect(bodyRows.length).toBe(rows.length)
  })

  it('expands a row when clicked', async () => {
    const wrapper = mountTable()
    const firstRow = wrapper.findAll('tbody tr')[0]
    await firstRow.trigger('click')
    expect(wrapper.emitted('expand')).toBeTruthy()
    expect(wrapper.emitted('expand')![0]).toEqual(['1'])
  })

  it('collapses an expanded row when clicked again', async () => {
    const wrapper = mountTable({ expandedIds: ['1'] })
    const firstRow = wrapper.findAll('tbody tr')[0]
    await firstRow.trigger('click')
    expect(wrapper.emitted('collapse')).toBeTruthy()
    expect(wrapper.emitted('collapse')![0]).toEqual(['1'])
  })

  it('supports multiple expanded rows simultaneously', async () => {
    const wrapper = mountTable({ expandedIds: ['1', '2'] })
    const detailCards = wrapper.findAll('.detail-card')
    expect(detailCards.length).toBe(2)
  })

  it('renders expanded row slot content', () => {
    const wrapper = mount(ExpandableTable as any, {
      props: { columns, rows, expandedIds: ['1'] },
      slots: {
        'expanded-row': `<template #expanded-row="{ row }"><div class="custom-detail">{{ row.status }}</div></template>`,
      },
    })
    expect(wrapper.find('.custom-detail').text()).toBe('published')
  })
})
