<template>
  <router-view />
</template>

<style>
/* Global dark theme styles */
html {
  scroll-behavior: smooth;
}

::selection {
  background-color: rgba(124, 58, 237, 0.4);
  color: #fff;
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}
::-webkit-scrollbar-track {
  background: #0f0f23;
}
::-webkit-scrollbar-thumb {
  background: #3f3f5f;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: #5b5b7a;
}

/* Focus visible styles */
*:focus-visible {
  outline: 2px solid #7c3aed;
  outline-offset: 2px;
}
</style>
