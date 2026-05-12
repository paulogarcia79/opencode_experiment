<template>
  <div>
    <!-- Page Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-2xl font-display font-bold text-white">Team Members</h1>
        <p class="mt-1 text-sm text-slate-500">Manage your team and invite new members</p>
      </div>
      <button
        @click="showInviteModal = true"
        class="inline-flex items-center gap-2 px-4 py-2.5 bg-primary-600 hover:bg-primary-500 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 hover:shadow-primary-500/30 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Invite User
      </button>
    </div>

    <!-- Global Error/Success Messages -->
    <div v-if="error" class="mb-6 border border-red-500/20 bg-red-500/10 rounded-xl p-4 flex items-start gap-3">
      <svg class="h-5 w-5 text-red-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <div class="flex-1">
        <p class="text-sm font-medium text-red-300">Error</p>
        <p class="text-sm text-red-400/80 mt-0.5">{{ error }}</p>
      </div>
      <button @click="error = ''" class="text-red-400 hover:text-red-300 cursor-pointer">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div v-if="success" class="mb-6 border border-emerald-500/20 bg-emerald-500/10 rounded-xl p-4 flex items-start gap-3">
      <svg class="h-5 w-5 text-emerald-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
      </svg>
      <div class="flex-1">
        <p class="text-sm font-medium text-emerald-300">Success</p>
        <p class="text-sm text-emerald-400/80 mt-0.5">{{ success }}</p>
      </div>
      <button @click="success = ''" class="text-emerald-400 hover:text-emerald-300 cursor-pointer">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center gap-3 text-slate-500 py-20">
      <svg class="animate-spin h-5 w-5 text-primary-500" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
      </svg>
      <span class="font-mono text-sm">Loading team members...</span>
    </div>

    <!-- Users Table -->
    <div v-else class="rounded-xl border border-white/5 bg-white/[0.02] overflow-hidden">
      <table class="w-full text-sm">
        <thead class="border-b border-white/5">
          <tr>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Email</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Role</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Status</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Active</th>
            <th class="px-5 py-4 text-left font-medium text-slate-500 text-xs uppercase tracking-wider">Joined</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-white/5">
          <tr
            v-for="user in users"
            :key="user.id"
            :class="[
              'transition-colors duration-150',
              user.is_active ? 'hover:bg-white/[0.02]' : 'opacity-50',
            ]"
          >
            <td class="px-5 py-4">
              <span class="font-medium text-white">{{ user.email }}</span>
            </td>
            <td class="px-5 py-4">
              <select
                v-if="roleLoadingId !== user.id"
                :value="user.role"
                @change="handleRoleChange(user.id, ($event.target as HTMLSelectElement).value)"
                class="bg-white/5 border border-white/10 text-white text-sm rounded-md px-2 py-1 focus:outline-none focus:border-primary-500/50 focus:ring-1 focus:ring-primary-500/20 cursor-pointer"
              >
                <option value="admin">Admin</option>
                <option value="editor">Editor</option>
                <option value="contributor">Contributor</option>
              </select>
              <span v-else class="inline-flex items-center gap-1.5 text-slate-400">
                <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Saving...
              </span>
            </td>
            <td class="px-5 py-4">
              <span
                :class="[
                  'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium',
                  user.is_verified
                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                    : 'bg-amber-500/10 text-amber-400 border border-amber-500/20',
                ]"
              >
                <span
                  :class="[
                    'w-1.5 h-1.5 rounded-full',
                    user.is_verified ? 'bg-emerald-400' : 'bg-amber-400',
                  ]"
                />
                {{ user.is_verified ? 'Verified' : 'Pending' }}
              </span>
            </td>
            <td class="px-5 py-4">
              <button
                v-if="activeLoadingId !== user.id"
                @click="handleToggleActive(user)"
                :class="[
                  'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border cursor-pointer transition-colors duration-200',
                  user.is_active
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20'
                    : 'bg-slate-500/10 text-slate-400 border-slate-500/20 hover:bg-slate-500/20',
                ]"
              >
                <span
                  :class="[
                    'w-1.5 h-1.5 rounded-full',
                    user.is_active ? 'bg-emerald-400' : 'bg-slate-500',
                  ]"
                />
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </button>
              <span v-else class="inline-flex items-center gap-1.5 text-slate-400">
                <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Updating...
              </span>
            </td>
            <td class="px-5 py-4 font-mono text-xs text-slate-500">
              {{ formatDate(user.created_at) }}
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="users.length === 0" class="px-6 py-16 text-center">
        <div class="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
          <svg class="w-7 h-7 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
        </div>
        <p class="text-slate-500 font-mono text-sm">No team members yet.</p>
        <p class="text-slate-600 text-sm mt-1">Invite your first team member to get started.</p>
      </div>
    </div>

    <!-- Invite Modal -->
    <div v-if="showInviteModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/60 backdrop-blur-sm"
        @click="closeInviteModal"
      />

      <!-- Modal -->
      <div class="relative w-full max-w-md mx-4 rounded-2xl border border-white/10 bg-surface-950 shadow-2xl shadow-black/40">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-display font-semibold text-white">Invite Team Member</h2>
            <button
              @click="closeInviteModal"
              class="text-slate-500 hover:text-white transition-colors duration-200 cursor-pointer"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="handleInvite" class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Email</label>
              <input
                v-model="inviteEmail"
                type="email"
                required
                placeholder="new-member@example.com"
                :disabled="inviteLoading"
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder-slate-600 focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-400 mb-2">Role</label>
              <select
                v-model="inviteRole"
                :disabled="inviteLoading"
                class="w-full px-4 py-3 rounded-lg bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20 transition-all duration-200 cursor-pointer"
              >
                <option value="admin">Admin</option>
                <option value="editor">Editor</option>
                <option value="contributor">Contributor</option>
              </select>
            </div>

            <div v-if="inviteError" class="text-sm text-red-400">
              {{ inviteError }}
            </div>

            <div class="flex gap-3 pt-2">
              <button
                type="button"
                @click="closeInviteModal"
                :disabled="inviteLoading"
                class="flex-1 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium rounded-lg transition-all duration-200 cursor-pointer disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="inviteLoading || !inviteEmail"
                class="flex-1 inline-flex items-center justify-center gap-2 px-4 py-3 bg-primary-600 hover:bg-primary-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-lg shadow-primary-600/20 cursor-pointer"
              >
                <svg v-if="inviteLoading" class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <span v-if="inviteLoading">Sending...</span>
                <span v-else>Send Invite</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchUsers, inviteUser, updateUserRole, toggleUserActive } from '@/composables/useAdminApi'
import type { User } from '@/types'

const users = ref<User[]>([])
const loading = ref(true)
const error = ref('')
const success = ref('')

const showInviteModal = ref(false)
const inviteEmail = ref('')
const inviteRole = ref('contributor')
const inviteLoading = ref(false)
const inviteError = ref('')

const roleLoadingId = ref<string | null>(null)
const activeLoadingId = ref<string | null>(null)

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}

async function loadUsers() {
  try {
    users.value = await fetchUsers()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to load users'
  } finally {
    loading.value = false
  }
}

function closeInviteModal() {
  showInviteModal.value = false
  inviteEmail.value = ''
  inviteRole.value = 'contributor'
  inviteError.value = ''
}

async function handleInvite() {
  inviteLoading.value = true
  inviteError.value = ''

  try {
    await inviteUser(inviteEmail.value, inviteRole.value)
    success.value = `Invite sent to ${inviteEmail.value}`
    closeInviteModal()
    await loadUsers()
  } catch (e: unknown) {
    inviteError.value = e instanceof Error ? e.message : 'Failed to send invite'
  } finally {
    inviteLoading.value = false
  }
}

async function handleRoleChange(userId: string, newRole: string) {
  roleLoadingId.value = userId
  error.value = ''

  try {
    await updateUserRole(userId, newRole)
    success.value = 'Role updated successfully'
    await loadUsers()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to update role'
  } finally {
    roleLoadingId.value = null
  }
}

async function handleToggleActive(user: User) {
  if (user.is_active && !confirm(`Deactivate ${user.email}?`)) return

  activeLoadingId.value = user.id
  error.value = ''

  try {
    await toggleUserActive(user.id, !user.is_active)
    success.value = `User ${user.is_active ? 'deactivated' : 'activated'}`
    await loadUsers()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : 'Failed to update user status'
  } finally {
    activeLoadingId.value = null
  }
}

onMounted(loadUsers)
</script>
