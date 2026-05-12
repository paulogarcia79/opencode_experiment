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
import AdminSettingsView from '@/views/AdminSettingsView.vue'
import AdminLayout from '@/components/AdminLayout.vue'
import AdminArticlesView from '@/views/AdminArticlesView.vue'
import AdminAnalyticsView from '@/views/AdminAnalyticsView.vue'
import AdminArticleEditView from '@/views/AdminArticleEditView.vue'
import AdminMediaView from '@/views/AdminMediaView.vue'
import AdminTagsView from '@/views/AdminTagsView.vue'
import AdminImportView from '@/views/AdminImportView.vue'
import AdminUsersView from '@/views/AdminUsersView.vue'
import SearchView from '@/views/SearchView.vue'
import TagArticlesView from '@/views/TagArticlesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/articles/:slug',
      name: 'article',
      component: ArticleView,
    },
    {
      path: '/confirm',
      name: 'confirm',
      component: ConfirmView,
    },
    {
      path: '/unsubscribe',
      name: 'unsubscribe',
      component: UnsubscribeView,
    },
    {
      path: '/search',
      name: 'search',
      component: SearchView,
    },
    {
      path: '/tags/:slug',
      name: 'tag-articles',
      component: TagArticlesView,
    },
    {
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLoginView,
      meta: { public: true },
    },
    {
      path: '/admin/forgot-password',
      name: 'admin-forgot-password',
      component: ForgotPasswordView,
      meta: { public: true },
    },
    {
      path: '/admin/reset-password',
      name: 'admin-reset-password',
      component: ResetPasswordView,
      meta: { public: true },
    },
    {
      path: '/admin/verify-email',
      name: 'admin-verify-email',
      component: VerifyEmailView,
      meta: { public: true },
    },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'admin-articles',
          component: AdminArticlesView,
        },
        {
          path: 'articles/new',
          name: 'admin-article-new',
          component: AdminArticleEditView,
        },
        {
          path: 'articles/:id/edit',
          name: 'admin-article-edit',
          component: AdminArticleEditView,
        },
        {
          path: 'media',
          name: 'admin-media',
          component: AdminMediaView,
        },
        {
          path: 'import',
          name: 'admin-import',
          component: AdminImportView,
        },
        {
          path: 'tags',
          name: 'admin-tags',
          component: AdminTagsView,
        },
        {
          path: 'analytics',
          name: 'admin-analytics',
          component: AdminAnalyticsView,
        },
        {
          path: 'settings',
          name: 'admin-settings',
          component: AdminSettingsView,
        },
        {
          path: 'users',
          name: 'admin-users',
          component: AdminUsersView,
          meta: { requiresAdmin: true },
        },
      ],
    },
  ],
})

let meFetched = false

router.beforeEach(async (to, _from, next) => {
  const store = useAdminStore()
  if (to.meta.requiresAuth && !store.token) {
    next('/admin/login')
  } else if (to.path === '/admin/login' && store.token) {
    next('/admin')
  } else {
    if (to.meta.requiresAuth && store.token && store.user === null && !meFetched) {
      meFetched = true
      await store.fetchMe()
      if (!store.token) {
        next('/admin/login')
        return
      }
    }
    if (to.meta.requiresAdmin && store.user?.role !== 'admin') {
      next('/admin')
      return
    }
    next()
  }
})

export default router
