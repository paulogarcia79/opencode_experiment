<template>
  <div class="min-h-screen bg-surface-950 flex items-center justify-center relative overflow-hidden">
    <!-- Background decorations -->
    <div class="absolute top-1/4 left-1/4 w-72 h-72 bg-emerald-600/10 rounded-full blur-3xl" />
    <div class="absolute bottom-1/4 right-1/4 w-72 h-72 bg-primary-600/10 rounded-full blur-3xl" />

    <div class="relative w-full max-w-md mx-4 text-center">
      <div class="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mx-auto mb-6">
        <svg class="h-8 w-8 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
      <h1 class="text-2xl font-display font-bold text-white">Subscription Confirmed</h1>
      <p class="mt-3 text-slate-400 leading-relaxed">
        You're all set! You'll receive our next newsletter with the latest articles on tech and games.
      </p>
      <RouterLink
        to="/"
        class="mt-8 inline-flex items-center gap-2 px-5 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-sm font-medium text-slate-300 rounded-lg transition-all duration-200 cursor-pointer"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
        </svg>
        Back to blog
      </RouterLink>
    </div>
  </div>
</template>
