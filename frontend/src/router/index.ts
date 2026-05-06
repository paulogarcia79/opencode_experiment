import { createRouter, createWebHistory } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import HomeView from '@/views/HomeView.vue'
import ArticleView from '@/views/ArticleView.vue'
import ConfirmView from '@/views/ConfirmView.vue'
import UnsubscribeView from '@/views/UnsubscribeView.vue'
import AdminLoginView from '@/views/AdminLoginView.vue'
import AdminLayout from '@/components/AdminLayout.vue'
import AdminArticlesView from '@/views/AdminArticlesView.vue'
import AdminArticleEditView from '@/views/AdminArticleEditView.vue'

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
      path: '/admin/login',
      name: 'admin-login',
      component: AdminLoginView,
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
      ],
    },
  ],
})

router.beforeEach((to, from, next) => {
  const store = useAdminStore()
  if (to.meta.requiresAuth && !store.token) {
    next('/admin/login')
  } else if (to.path === '/admin/login' && store.token) {
    next('/admin')
  } else {
    next()
  }
})

export default router
