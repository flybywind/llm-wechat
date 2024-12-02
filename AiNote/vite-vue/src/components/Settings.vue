<script setup>
import { ref, watch } from 'vue'

const accessKeys = ref({
  qianfan: {
    accessKey: '',
    secretKey: ''
  },
  tongyi: {
    accessKey: ''
  }
})

watch(accessKeys, (newVal) => {
  console.log(JSON.stringify(newVal))
},
{
  deep: true
})
</script>

<template>
  <div class="setting">
    <div class="api-keys">
      <ul>
        <li class="flex-vert">
          <h3>千帆</h3>
          <div class="item">
            <label>Access Key</label>
            <input type="text" v-model="accessKeys.qianfan.accessKey">
          </div>
          <div class="item">
            <label>Secret Key</label>
            <input type="text" v-model="accessKeys.qianfan.secretKey">
          </div>
        </li>
        <li class="flex-vert">
          <h3>通义</h3>
          <div class="item">
            <label>Access Key</label>
            <input type="text" v-model="accessKeys.tongyi.accessKey">
          </div>
        </li>
      </ul>
    </div>
</div>

</template>

<style lang="scss" scoped>
  .api-keys {
    .item {
      border-bottom: $text-color 1px solid;
      ;
    }
    li {
      label {
        font-weight: bold;
        padding-right: 1em;
      }
    }
  }
</style>
