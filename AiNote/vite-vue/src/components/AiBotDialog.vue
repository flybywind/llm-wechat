<script setup>
import OpenAI from "openai/index.mjs";
import { computed, ref, reactive, useTemplateRef } from "vue";
import Chat from "./Chat.vue";

const openai = new OpenAI({
  baseURL: "https://api.openai.com/v1",
});
// var chatList = [
//   {
//     id: 0,
//     name: "You",
//     type: "user",
//     timestamp: "2021-02-01 00:00:00",
//     content: "answer My question",
//   },
//   {
//     id: 1,
//     name: "AI",
//     type: "ai",
//     timestamp: "2021-01-04 00:00:00",
//     content: "## Hello Vue 3 + Vite\n\n*code:*\n\n```python\nprint('Hello World')\n```",
//   },
// ];
const chatListRef = reactive([]);
var intervalId = ref(null);
var textarea = useTemplateRef("textarea");
var sendBtnClass = computed(() => (intervalId.value !== null ? "stop" : "send"));
function askQuestion(idx) {
  if (sendBtnClass.value === "stop") {
    pywebview.api.stop_answering();
    return;
  }

  const q = idx==-1 ? textarea.value.value:chatListRef[idx].content;
  textarea.value.value = "";
  pywebview.api.add_or_update_question(idx, q).then((new_chats) => {
    const [newQuestion, newAnswer] = new_chats;
    if (idx == -1) {
      chatListRef.push(newQuestion);
      chatListRef.push(newAnswer);
    } else {
      Object.assign(chatListRef[idx], newQuestion);
      Object.assign(chatListRef[idx+1], newAnswer);
    }

    intervalId.value = setInterval(() => {
      pywebview.api
        .get_answer()
        .then((info) => {
          if (info.content !== "<END>") {
            Object.assign(chatListRef[info.id], info);
          } else {
            clearInterval(intervalId.value);
            intervalId.value = null;
          }
        })
        .catch((err) => {
          console.error(err);
        });
    }, 100);
  });
}

const handleInfoUpdate = (newInfo) => {
  const idx = newInfo.id;
  chatListRef[idx] = newInfo;
  console.log("content changed at ", idx);
  if (newInfo.type === "user") {
    askQuestion(idx);
  }
};
</script>

<template>
  <div class="dialog">
    <div class="flex-root">
      <div class="side-bar">
        <h3>收藏历史</h3>
        <div class="history"></div>
      </div>
      <div class="dialog-window">
        <div class="session">
          <Chat v-for="chat in chatListRef" :Info="chat" :status="sendBtnClass" @updateContent="handleInfoUpdate">
          </Chat>
        </div>
        <div class="send-chat">
          <div class="wrapper">
            <textarea ref="textarea"></textarea>
            <button :class="sendBtnClass" @click="askQuestion(-1)"></button>
          </div>
        </div>
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

.flex-root {
  width: 100%;

  .dialog-window {
    display: flex;
    flex: 5;
    flex-direction: column;
    align-items: stretch;
    padding-left: 3px;
    border-left: $secondary-color 2px solid;

    .session {
      flex: 10;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      margin-left: 10px;
      padding: 2rem;
    }

    .send-chat {
      min-height: 4em;
      position: relative;

      .wrapper {
        position: absolute;
        bottom: 3px;
        right: 10px;
        padding: 1rem;
        display: flex;
        width: 100%;

        textarea {
          flex: 5;
          border: none;
          border-radius: 4px;
          padding: 0.5rem;
          margin-right: 1rem;
        }

        button {
          border-radius: 2px;
          width: 5em;

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
  }
}
</style>
