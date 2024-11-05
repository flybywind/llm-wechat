<template>
  <div :class="`one-chat role-${info.type}`">
    <div class="container">
      <div class="header">
        <span class="name">{{ info.name }}</span>
        <span class="timestamp">{{ `[${info.timestamp}]` }}</span>
      </div>
      <div class="sentence" v-html="markdownContent.value"></div>
    </div>
  </div>
</template>

<script setup>
  import { defineProps, defineExpose, ref, computed } from "vue";
  const props = defineProps({
    Info: {
      type: Object,
      default: () => ({
        id: 0,
        name: "AI",
        type: "ai",
        timestamp: "2021-01-01 00:00:00",
      }),
    },
  });

  var info = ref(props.Info);
  var rawContent = ref("");
  const markdownContent = computed(() =>{
    return rawContent;
  })

  function updateContent(content) {
    rawContent.value += content;
  }
  function getChatId() {
    return info.value.id;
  }
  defineExpose({
    updateContent,
    getChatId,
  });
</script>
<style lang="scss" scoped>
  .one-chat {
    display: flex;
    width: 100%;
    &.role-ai {
      justify-content: flex-start;
      background-color: $background-color;
    }
    &.role-user {
      justify-content: flex-end;
      max-width: 100%;

      .sentence {
        border-bottom: $primary-color 1px solid;
      }
      .container {
        background-color: $user-background-color;
      }
    }
    .container {
      display: flex;
      flex-direction: column;
    }
    .header {
      padding: 0.5em;
    }

    .timestamp {
      font-size: 0.9em;
    }
  }
</style>
