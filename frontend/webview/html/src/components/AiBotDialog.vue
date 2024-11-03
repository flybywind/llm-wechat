<template>
  <div class="flex-root">
    <div class="side-bar">
      <h1>{{ msg }}</h1>
      <button @click="count++">Count is: {{ count }}</button>
    </div>
    <div class="dialog-window">
      <h1>{{ msg }}</h1>
      <button @click="count++">Count is: {{ count }}</button>
    </div>
  </div>
</template>

<script setup>
  import { ref } from "vue";

  defineProps({
    msg: {
      type: String,
      default: "Hello Vue 3 + Vite",
    },
  });

  const count = ref(0);
</script>

<style lang="scss" scoped>
  .side-bar {
    flex: 1;
    height: 100%;
    padding: 2rem;

    h1 {
      color: $primary-color;
      margin-bottom: 1rem;
    }

    button {
      background-color: $secondary-color;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;

      &:hover {
        opacity: 0.9;
      }
    }

    @include responsive(tablet) {
      padding: 3rem;
    }
  }
  .dialog-window {
    flex: 5;
    border-left: $secondary-color 2px solid;
    margin-left: 10px;
    padding: 2rem;
    height: 100%;
  }
</style>
