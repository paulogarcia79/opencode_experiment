import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import AdminUsersView from '@/views/AdminUsersView.vue'

vi.mock('@/composables/useAdminApi', () => ({
  fetchUsers: vi.fn(),
  inviteUser: vi.fn(),
  updateUserRole: vi.fn(),
  toggleUserActive: vi.fn(),
}))

import { fetchUsers, inviteUser, updateUserRole, toggleUserActive } from '@/composables/useAdminApi'

const mockUsers = [
  {
    id: 'user-1',
    email: 'admin@example.com',
    role: 'admin',
    is_active: true,
    is_verified: true,
    created_at: '2025-01-15T00:00:00Z',
  },
  {
    id: 'user-2',
    email: 'editor@example.com',
    role: 'editor',
    is_active: true,
    is_verified: true,
    created_at: '2025-02-20T00:00:00Z',
  },
  {
    id: 'user-3',
    email: 'pending@example.com',
    role: 'contributor',
    is_active: false,
    is_verified: false,
    created_at: '2025-03-10T00:00:00Z',
  },
]

describe('AdminUsersView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true))
  })

  it('shows loading state while fetching', () => {
    vi.mocked(fetchUsers).mockImplementation(() => new Promise(() => {}))

    const wrapper = mount(AdminUsersView)

    expect(wrapper.text()).toContain('Loading team members...')
  })

  it('shows empty state when no users', async () => {
    vi.mocked(fetchUsers).mockResolvedValue([])

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    expect(wrapper.text()).toContain('No team members yet')
  })

  it('renders user list with email, role, status, and active state', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    expect(wrapper.text()).toContain('admin@example.com')
    expect(wrapper.text()).toContain('editor@example.com')
    expect(wrapper.text()).toContain('pending@example.com')
    expect(wrapper.text()).toContain('Verified')
    expect(wrapper.text()).toContain('Pending')
    expect(wrapper.text()).toContain('Active')
    expect(wrapper.text()).toContain('Inactive')
  })

  it('shows inactive users with reduced opacity', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const rows = wrapper.findAll('tbody tr')
    const inactiveRow = rows.find(row => row.text().includes('pending@example.com'))
    expect(inactiveRow?.classes()).toContain('opacity-50')
  })

  it('opens invite modal when clicking Invite User button', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const inviteBtn = wrapper.findAll('button').find(btn => btn.text().includes('Invite User'))
    await inviteBtn?.trigger('click')

    expect(wrapper.text()).toContain('Invite Team Member')
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
  })

  it('sends invite on form submission', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)
    vi.mocked(inviteUser).mockResolvedValue({ message: 'Invite sent' })

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const inviteBtn = wrapper.findAll('button').find(btn => btn.text().includes('Invite User'))
    await inviteBtn?.trigger('click')

    const emailInput = wrapper.find('input[type="email"]')
    await emailInput.setValue('new@example.com')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(inviteUser).toHaveBeenCalledWith('new@example.com', 'contributor')
  })

  it('shows error on invite failure', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)
    vi.mocked(inviteUser).mockRejectedValue(new Error('User already exists'))

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const inviteBtn = wrapper.findAll('button').find(btn => btn.text().includes('Invite User'))
    await inviteBtn?.trigger('click')

    const emailInput = wrapper.find('input[type="email"]')
    await emailInput.setValue('existing@example.com')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('User already exists')
  })

  it('calls updateUserRole when role dropdown changes', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)
    vi.mocked(updateUserRole).mockResolvedValue({ message: 'Role updated' })

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const select = wrapper.find('select')
    await select.setValue('editor')
    await flushPromises()

    expect(updateUserRole).toHaveBeenCalledWith('user-1', 'editor')
  })

  it('calls toggleUserActive when active button clicked', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)
    vi.mocked(toggleUserActive).mockResolvedValue({ message: 'User deactivated' })

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const activeBtns = wrapper.findAll('button').filter(btn =>
      btn.text().includes('Active') || btn.text().includes('Inactive')
    )
    await activeBtns[0]?.trigger('click')
    await flushPromises()

    expect(toggleUserActive).toHaveBeenCalledWith('user-1', false)
  })

  it('shows confirmation before deactivating user', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)
    vi.mocked(toggleUserActive).mockResolvedValue({ message: 'User deactivated' })
    vi.mocked(globalThis.confirm).mockReturnValue(false)

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const activeBtns = wrapper.findAll('button').filter(btn =>
      btn.text().includes('Active')
    )
    await activeBtns[0]?.trigger('click')
    await flushPromises()

    expect(toggleUserActive).not.toHaveBeenCalled()
  })

  it('shows success message after successful action', async () => {
    vi.mocked(fetchUsers).mockResolvedValue(mockUsers)
    vi.mocked(inviteUser).mockResolvedValue({ message: 'Invite sent' })

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    const inviteBtn = wrapper.findAll('button').find(btn => btn.text().includes('Invite User'))
    await inviteBtn?.trigger('click')

    const emailInput = wrapper.find('input[type="email"]')
    await emailInput.setValue('new@example.com')

    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Invite sent to new@example.com')
  })

  it('shows error state on fetch failure', async () => {
    vi.mocked(fetchUsers).mockRejectedValue(new Error('Network error'))

    const wrapper = mount(AdminUsersView)
    await flushPromises()

    expect(wrapper.text()).toContain('Error')
    expect(wrapper.text()).toContain('Network error')
  })
})
