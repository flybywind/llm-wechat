<script setup>
  import { computed, ref, useTemplateRef, watch } from "vue";
  import Chat from './Chat.vue';
  import fnv1a from "../utils/hash";
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
  var intervalId = ref(-1);
  var textarea = ref(null)
  var sendBtnClass = computed(() => intervalId.value !== -1 ? "stop":"send");
  function askQuestion() {
    const q = textarea.value;
    const [newQuestion, newAnswer] = pywebview.api.add_or_update_question(-1, q.value)
    chatListRef.value.append(newQuestion)
    chatListRef.value.append(newAnswer)
    intervalId = setInterval(() => {
      if (pywebview.api.get_answer() !== "<END>") {
        chatCompRef.value[id].updateContent(pywebview.api.get_answer());
      } else {
        clearInterval(intervalId);
        intervalId.value = -1;
      }
    }, 100);
  }
  const contentHash = computed(() => {
    chatListRef.value.map((info) => {
      // return hash code of the info.content
      return {id: info.id, type:info.type, hash: fnv1a(info.content)};
    });
  });

  watch(contentHash, 
  (newVal, oldVal) => {
    const ln = newVal.length;
    for (let i = 0; i < ln; i++) {
      if (newVal[i].hash !== oldVal[i].hash) {
        const id = newVal[i].id;
        if (newVal[i].type === "user"){
          const question = chatListRef.value[id].content;  
          pywebview.api.add_or_update_question(i, question);  
          intervalId = setInterval(() => {
            if (window.pywebview.api.getAnswer() !== "<END>") {
              chatCompRef.value[id].updateContent(pywebview.api.get_answer());
            } else {
              clearInterval(intervalId);
              intervalId.value = -1;
            }
          }, 100);
        }
      } 
    }
  }, 
  {deep: true}
  );
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
        <textarea ref="textarea"></textarea>
        <button :class="sendBtnClass" @click="askQuestion"></button>
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
    display: flex;
    flex-direction: column;
    align-items: stretch;
    border-left: $secondary-color 2px solid;
    margin-left: 10px;
    padding: 2rem;
    height: 100%;

    .send-chat {
      display: flex;
      min-height: 4em;
      textarea {
        flex: 5;
        border: none;
        border-radius: 4px;
        padding: 0.5rem;
        margin-right: 1rem;
      }
      button {
        flex: 1;
        border-radius: 2px;
        &:hover {
          box-shadow: 3px 3px 3px $inactive-color;
        }
        &.stop::after {
          content: "停止";
        }
        &.stop {
          background-color: $inactive-color;
          color: $secondary-color;
        }
        &.send::after {
          content: "发送";
        }
        &.send {
          background-color: #c3deff;
          color: $text-color;
        }
      }
    }
  }
</style>
