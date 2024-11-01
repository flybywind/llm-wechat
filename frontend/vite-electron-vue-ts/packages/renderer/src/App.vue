<template>
  <div class="flex flex-col h-screen bg-gray-100">
    <div ref="chatContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
      <div v-for="(message, index) in messages" :key="index"
        :class="['flex', message.role === 'user' ? 'justify-end' : 'justify-start']">
        <div :class="[
          'max-w-[70%] rounded-lg p-4',
          message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-white text-gray-800'
        ]">
          <div v-html="renderMarkdown(message.content)" class="markdown-body"></div>
        </div>
      </div>
      <div ref="messagesEnd"></div>
    </div>

    <form @submit.prevent="handleSubmit" class="p-4 bg-white border-t">
      <div class="flex space-x-4">
        <input type="text" v-model="input" :disabled="isStreaming"
          class="flex-1 p-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Type your message...">
        <button type="submit" :disabled="isStreaming"
          class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50">
          Send
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import highlightjs from 'markdown-it-highlightjs'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

const md = new MarkdownIt().use(highlightjs)
const messages = ref<Message[]>([])
const input = ref('')
const isStreaming = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const messagesEnd = ref<HTMLElement | null>(null)

const scrollToBottom = async () => {
  await nextTick()
  messagesEnd.value?.scrollIntoView({ behavior: 'smooth' })
}

const renderMarkdown = (content: string): string => {
  return md.render(content)
}

onMounted(() => {
  scrollToBottom()
})

const handleSubmit = async () => {
  if (!input.value.trim()) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: input.value
  })
  
  const userInput = input.value
  input.value = ''
  
  // Add empty assistant message
  messages.value.push({
    role: 'assistant',
    content: ''
  })
  
  isStreaming.value = true
  
  try {
    const response = await fetch('YOUR_API_ENDPOINT', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages: messages.value.slice(0, -1)
      })
    })

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) throw new Error('No reader available')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      messages.value[messages.value.length - 1].content += chunk
      await scrollToBottom()
    }
  } catch (error) {
    console.error('Error:', error)
    messages.value[messages.value.length - 1].content += '\nError: Failed to get response.'
  } finally {
    isStreaming.value = false
    await scrollToBottom()
  }
}
</script>

<style>
.markdown-body {
  @apply text-sm leading-relaxed;
}

.markdown-body pre {
  @apply p-4 rounded-lg bg-gray-800 text-white overflow-x-auto;
}

.markdown-body code {
  @apply font-mono;
}

.markdown-body p {
  @apply my-2;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  @apply font-bold my-4;
}

.markdown-body ul,
.markdown-body ol {
  @apply pl-6 my-4;
}

.markdown-body ul {
  @apply list-disc;
}

.markdown-body ol {
  @apply list-decimal;
}
</style>