<template>
  <div id="app-shell">
    <nav class="topnav">
      <div class="topnav-inner">
        <router-link to="/" class="brand">
          <span class="brand-icon">⚡</span>
          <span class="brand-name">PlateauBreaker</span>
        </router-link>
        <div class="nav-links">
          <router-link
            to="/"
            class="nav-link"
            active-class="nav-link-active"
            exact-active-class="nav-link-active"
          >
            <i class="pi pi-chart-line" />
            <span>Dashboard</span>
          </router-link>
          <router-link
            to="/records"
            class="nav-link"
            active-class="nav-link-active"
            exact-active-class="nav-link-active"
          >
            <i class="pi pi-calendar" />
            <span>Records</span>
          </router-link>
          <router-link
            to="/analysis"
            class="nav-link"
            active-class="nav-link-active"
            exact-active-class="nav-link-active"
          >
            <i class="pi pi-search" />
            <span>Analysis</span>
          </router-link>
        </div>
      </div>
    </nav>
    <main class="main-content">
      <router-view />
    </main>
    <Toast position="top-right" />
  </div>
</template>

<script setup lang="ts">
import Toast from 'primevue/toast'
</script>

<style scoped>
#app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg);
}
.topnav {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255,255,255,0.96);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.topnav-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--color-text-primary);
}
.brand-icon { font-size: 1.3rem; }
.brand-name {
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.nav-links { display: flex; gap: 4px; }
.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all 0.15s ease;
}
.nav-link:hover { background: #f1f5f9; color: var(--color-text-primary); }
.nav-link-active { background: #eef2ff; color: var(--color-accent); font-weight: 600; }
.main-content { flex: 1; }
@media (max-width: 480px) {
  .nav-link span { display: none; }
  .nav-link { padding: 6px 10px; }
  .brand-name { display: none; }
}
</style>
