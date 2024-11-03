<script setup>
import AiBotDialog from './components/AiBotDialog.vue'
</script>

<template>
<div class="window flex-vert">
  <div class="header">
    <a href="https://vite.dev" target="_blank">
      <img src="/vite.svg" class="logo" alt="Vite logo" />
    </a>
    <a href="https://vuejs.org/" target="_blank">
      <img src="./assets/vue.svg" class="logo vue" alt="Vue logo" />
    </a>
  </div>
  <AiBotDialog class="dialog" msg="Vite + Vue" />
</div>
</template>

<style lang="scss" scoped>
.window {
  display: flex;
  height: 100vh;
}

.header {
  flex: 1;
  padding: 1em;
  width: 100%;
  border-bottom: $secondary-color 2px solid;
}

.dialog {
  @include flexCenter;
  flex: 10;
  padding: 1em;
  width: 100%;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}

.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}

.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
