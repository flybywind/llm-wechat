<script setup>
  import { ref, computed, useTemplateRef, watch } from "vue";
  import SmartMarkdownConverter from "../utils/smart_markdown";
  const converter = new SmartMarkdownConverter();
  const props = defineProps({
    Info: {
      type: Object,
      default: () => ({
        id: 0,
        name: "AI",
        type: "ai",
        timestamp: 1700000000,
        content: "Hello, World!",
      }),
    },
  });

  var info = ref(props.Info);
  const editting = ref(false);
  const questionEditting = useTemplateRef("questionEditting");
  const questionMarkdown = useTemplateRef("questionMarkdown");
  var timestamp_str = computed(() => {
    const date = new Date(info.value.timestamp);
    return date.toLocaleString();
  });
  const markdownContent = computed(() =>{
    if (info.value.type === "user") {
      // todo, 支持回车换行。和markdown的换行方式不一样。markdown是2个回车1个换行。
      // 这里则需要根据用户习惯，一个回车即可换行
      return info.value.content;
    }
    const html = converter.convert(info.value.content);
    return html;
  })

  watch(editting, (newVal) => {
    if (newVal) {
      questionMarkdown.value.style.display = "none";
      questionEditting.value.style.display = "block";
      questionEditting.value.value = info.value.content;
      questionEditting.value.focus();
    } else {
      questionEditting.value.style.display = "none";
      questionMarkdown.value.style.display = "block";
      info.value.content = questionEditting.value.value;
    }
  });
</script>

<template>
  <div :class="`one-chat role-${info.type}`">
    <div class="container">
      <div class="header">
        <span class="name">{{ info.name }}</span>
        <span class="timestamp">{{ `[${timestamp_str}]` }}</span>
      </div>
      <div class="sentence">
        <div class="content" v-html="markdownContent" ref="questionMarkdown"></div>
        <textarea ref="questionEditting" @blur="editting=false"></textarea>
      </div>
      <div class="edit-button" @click="editting=true">
        <font-awesome-icon icon="pencil-alt" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
  .one-chat {
    display: flex;
    width: 100%;
    &.role-ai {
      justify-content: flex-start;
      background-color: $background-color;
      .edit-button {
        display: none;
      }
    }
    &.role-user {
      justify-content: flex-end;
      max-width: 100%;
      .sentence {
        border-bottom: $primary-color 1px solid;
      }
      .container {
        position: relative;
        cursor: pointer;
        background-color: $user-background-color;

        .edit-button {
          position: absolute;
          right: 0;
          bottom: 0;
          scale: 0.7;
          opacity: 0;
          transition: opacity 0.3s ease-in-out;
          transform: translateX(1.5em);
        }

        /* 鼠标悬停时显示编辑按钮 */
        &:hover .edit-button {
          opacity: 1;
        }
      }
    }
    .container {
      display: flex;
      flex-direction: column;
      .sentence {
        textarea {
          display: none;
          width: 100%;
          height: 100%;
          border: none;
          background-color: $user-background-color;
          resize: none;
          font-size: 1em;
        }
      }
    }
    .header {
      padding: 0.5em;
    }

    .timestamp {
      padding: 0 0.3em;
      font-size: 0.8em;
    }
  }
</style>
