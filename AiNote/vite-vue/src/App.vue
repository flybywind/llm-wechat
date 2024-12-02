<script setup>
</script>

<template>
<div class="window flex-vert">
  <div class="header">
    <nav>
      <router-link to="/">Home</router-link> |
      <router-link to="/Settings">Settings</router-link> |
    </nav>
  </div>
  <router-view></router-view>
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
