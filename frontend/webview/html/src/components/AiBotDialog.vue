<script setup>
  import { onMounted, ref, useTemplateRef } from "vue";
  import Chat from './Chat.vue';
  defineProps({
    msg: {
      type: String,
      default: "Hello Vue 3 + Vite",
    },
  });

  var chatList = [{
    id: 0,
    name: "You",
    type: "user",
    timestamp: "2021-02-01 00:00:00",
    content: "answer My question",
  },{
    id: 1,
    name: "AI",
    type: "ai",
    timestamp: "2021-01-04 00:00:00",
    content: "## Hello Vue 3 + Vite\n\n*code:*\n\n```python\nprint('Hello World')\n```",
  }];
  const chatListRef = ref(chatList);
  var chatCompRef = useTemplateRef('chatCompRef');
  onMounted(() => {
    chatCompRef.value.forEach((comp) => {
      const id = comp.getChatId();
      comp.updateContent(chatList[id].content);
    });
  });
</script>

<template>
  <div class="flex-root">
    <div class="side-bar">
      <h3>收藏历史</h3>
      <div class="history"></div>
    </div>
    <div class="dialog-window">
      <Chat v-for="chat in chatListRef" :Info="chat" ref="chatCompRef"></Chat>
      <div class="send-chat">
      <textarea ></textarea>
      <button >发送</button>
      </div>
    </div>
  </div>
</template>


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
      color: rgb(160, 32, 32);
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
