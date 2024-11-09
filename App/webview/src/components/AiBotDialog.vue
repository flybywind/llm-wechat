<script setup>
import { computed, ref, useTemplateRef, watch } from "vue";
import Chat from "./Chat.vue";
import fnv1a from "../utils/hash";
var chatList = [
  // {
  //   id: 0,
  //   name: "You",
  //   type: "user",
  //   timestamp: "2021-02-01 00:00:00",
  //   content: "answer My question",
  // },
  // {
  //   id: 1,
  //   name: "AI",
  //   type: "ai",
  //   timestamp: "2021-01-04 00:00:00",
  //   content: "## Hello Vue 3 + Vite\n\n*code:*\n\n```python\nprint('Hello World')\n```",
  // },
];
const chatListRef = ref(chatList);
var chatCompRef = useTemplateRef("chatCompRef");
var intervalId = ref(null);
var textarea = ref(null);
var sendBtnClass = computed(() => (intervalId.value !== null ? "stop" : "send"));
// setInterval(() => {
//     console.log(`send button class = ${sendBtnClass.value}`);
// }, 1000);
function askQuestion(idx) {
  const q = textarea.value;
  pywebview.api.add_or_update_question(idx, q.value).then((new_chats) => {
    const [newQuestion, newAnswer] = new_chats;
    chatListRef.value.push(newQuestion);
    chatListRef.value.push(newAnswer);

    intervalId.value = setInterval(() => {
      pywebview.api
        .get_answer()
        .then(info => {
          // console.log(`id = ${id}, content = ${content}, type = ${type}, timestamp = ${timestamp}`);
          if (info.content !== "<END>") {
            chatListRef.value[info.id] = info;
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
const contentHash = computed(() => {
  chatListRef.value.map((info) => {
    // return hash code of the info.content
    return {
      id: info.id,
      type: info.type,
      hash: fnv1a(info.content),
    };
  });
});

watch(
  contentHash,
  (newVal, oldVal) => {
    const ln = newVal.length;
    for (let i = 0; i < ln; i++) {
      if (newVal[i].hash !== oldVal[i].hash) {
        if (newVal[i].type === "user") {
          askQuestion(newVal[i].id);
        } else {
          throw new Error("only user's question can be updated");
        }
      }
    }
  },
  {
    deep: true,
  }
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
        <button :class="sendBtnClass" @click="askQuestion(-1)"></button>
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
