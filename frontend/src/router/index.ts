import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import HomeView from '@/views/HomeView.vue'
import ArticleView from '@/views/ArticleView.vue'
import ConfirmView from '@/views/ConfirmView.vue'
import UnsubscribeView from '@/views/UnsubscribeView.vue'
import AdminLoginView from '@/views/AdminLoginView.vue'
import ForgotPasswordView from '@/views/ForgotPasswordView.vue'
import ResetPasswordView from '@/views/ResetPasswordView.vue'
import VerifyEmailView from '@/views/VerifyEmailView.vue'
import SetupView from '@/views/SetupView.vue'
import AdminSettingsView from '@/views/AdminSettingsView.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import EditorDashboard from '@/components/EditorDashboard.vue'
import ContributorDashboard from '@/components/ContributorDashboard.vue'
import AdminArticlesView from '@/views/AdminArticlesView.vue'
import AdminAnalyticsView from '@/views/AdminAnalyticsView.vue'
import AdminArticleEditView from '@/views/AdminArticleEditView.vue'
import AdminMediaView from '@/views/AdminMediaView.vue'
import AdminTagsView from '@/views/AdminTagsView.vue'
import AdminImportView from '@/views/AdminImportView.vue'
import AdminUsersView from '@/views/AdminUsersView.vue'
import ContributorCardsView from '@/views/ContributorCardsView.vue'
import ReviewQueue from '@/views/ReviewQueue.vue'
import ArticlePreviewView from '@/views/ArticlePreviewView.vue'
import ForbiddenPage from '@/views/ForbiddenPage.vue'
import SearchView from '@/views/SearchView.vue'
import TagArticlesView from '@/views/TagArticlesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Public routes
    { path: '/', name: 'home', component: HomeView },
    { path: '/articles/:slug', name: 'article', component: ArticleView },
    { path: '/confirm', name: 'confirm', component: ConfirmView },
    { path: '/unsubscribe', name: 'unsubscribe', component: UnsubscribeView },
    { path: '/search', name: 'search', component: SearchView },
    { path: '/tags/:slug', name: 'tag-articles', component: TagArticlesView },

    // Auth pages
    { path: '/admin/login', name: 'admin-login', component: AdminLoginView, meta: { public: true } },
    { path: '/admin/forgot-password', name: 'admin-forgot-password', component: ForgotPasswordView, meta: { public: true } },
    { path: '/admin/reset-password', name: 'admin-reset-password', component: ResetPasswordView, meta: { public: true } },
    { path: '/admin/verify-email', name: 'admin-verify-email', component: VerifyEmailView, meta: { public: true } },
    { path: '/admin/setup', name: 'admin-setup', component: SetupView, meta: { public: true } },

    // Forbidden
    { path: '/forbidden', name: 'forbidden', component: ForbiddenPage, meta: { public: true } },

    // Admin namespace
    {
      path: '/admin',
      component: AdminDashboard,
      meta: { requiresAuth: true, allowedRoles: ['admin'] },
      children: [
        { path: '', name: 'admin-articles', component: AdminArticlesView },
        { path: 'articles/new', name: 'admin-article-new', component: AdminArticleEditView },
        { path: 'articles/:id/edit', name: 'admin-article-edit', component: AdminArticleEditView },
        { path: 'review', name: 'admin-review', component: ReviewQueue },
        { path: 'media', name: 'admin-media', component: AdminMediaView },
        { path: 'import', name: 'admin-import', component: AdminImportView },
        { path: 'tags', name: 'admin-tags', component: AdminTagsView },
        { path: 'analytics', name: 'admin-analytics', component: AdminAnalyticsView },
        { path: 'settings', name: 'admin-settings', component: AdminSettingsView },
        { path: 'users', name: 'admin-users', component: AdminUsersView },
      ],
    },

    // Editor namespace
    {
      path: '/editor',
      component: EditorDashboard,
      meta: { requiresAuth: true, allowedRoles: ['admin', 'editor'] },
      children: [
        { path: '', name: 'editor-articles', component: AdminArticlesView },
        { path: 'articles/new', name: 'editor-article-new', component: AdminArticleEditView },
        { path: 'articles/:id/edit', name: 'editor-article-edit', component: AdminArticleEditView },
        { path: 'review', name: 'editor-review', component: ReviewQueue },
        { path: 'import', name: 'editor-import', component: AdminImportView },
        { path: 'settings', name: 'editor-settings', component: AdminSettingsView },
      ],
    },

    // Contributor namespace
    {
      path: '/contributor',
      component: ContributorDashboard,
      meta: { requiresAuth: true, allowedRoles: ['admin', 'editor', 'contributor'] },
      children: [
        { path: '', name: 'contributor-articles', component: ContributorCardsView },
        { path: 'articles/new', name: 'contributor-article-new', component: AdminArticleEditView },
        { path: 'articles/:id/edit', name: 'contributor-article-edit', component: AdminArticleEditView },
        { path: 'import', name: 'contributor-import', component: AdminImportView },
        { path: 'articles/:id/preview', name: 'contributor-article-preview', component: ArticlePreviewView },
        { path: 'settings', name: 'contributor-settings', component: AdminSettingsView },
      ],
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const store = useAdminStore()

  // Public routes — allow through
  if (to.meta.public) {
    next()
    return
  }

  // Auth required but no token — redirect to login
  if (to.meta.requiresAuth && !store.token) {
    next('/admin/login')
    return
  }

  // Already logged in and visiting login — redirect to dashboard
  if (to.path === '/admin/login' && store.token) {
    if (!store.profileLoaded) {
      await store.fetchMe()
    }
    const role = store.user?.role ?? 'contributor'
    const dashboard: Record<string, string> = {
      admin: '/admin',
      editor: '/editor',
      contributor: '/contributor',
    }
    next(dashboard[role] || '/admin')
    return
  }

  // Load user profile if needed
  if (to.meta.requiresAuth && store.token && !store.profileLoaded) {
    await store.fetchMe()
    if (!store.token) {
      next('/admin/login')
      return
    }
  }

  // Role-based route guards
  if (to.meta.allowedRoles && store.user) {
    const allowedRoles = to.meta.allowedRoles as string[]
    if (!allowedRoles.includes(store.user.role)) {
      next('/forbidden')
      return
    }
  }

  // Cross-namespace editor redirect for article edit
  if (
    store.user?.role === 'editor' &&
    to.path.startsWith('/contributor/articles/') &&
    to.path.endsWith('/edit')
  ) {
    const articleId = to.params.id as string
    next(`/editor/articles/${articleId}/edit`)
    return
  }

  next()
})

export default router
