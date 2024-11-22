<template>
  <div>
    <RecursiveForm :schema="schema" :depth="0" @update:schema="value => schema = value" />
  </div>
</template>

<script setup>
import { ref, h } from 'vue';

const props = defineProps(['schema']);
const schema = ref(props.schema); 
const emit = defineEmits(['update:schema']);

const RecursiveForm = {
  props: {
    schema: {
      type: Object,
      required: true,
    },
    depth: {
      type: Number,
      required: true,
    },
  },
  render() {
    console.log(`got schema: ${JSON.stringify(this.schema)}, depth = ${this.depth}`);
    if (this.schema.type === 'object') {
      return h('details', [        
        h('summary', this.schema.repr_name || 'unknown'),
        h('div', { style: { marginLeft: `${this.depth * 20}px` } }, 
          Object.entries(this.schema.properties).map(([key, subSchema]) => {
            console.log(`sub schema: key = ${key}, schema = ${JSON.stringify(subSchema)}`)
            return h('div', [
              h('label', key),
              h(RecursiveForm, { 
                schema: subSchema, 
                depth: this.depth + 1, 
                on: {
                  'update:schema': value => {
                    this.schema.properties[key] = value;
                    this.$emit('update:schema', this.schema);
                  }
                }
              })
            ])
          }) 
        )
      ]);
    } else if (this.schema.type === 'array') {
      return h('select', {
        value: this.schema.default,
        onInput: event => {
          this.schema.default = event.target.value;
          this.$emit('update:schema', this.schema);
        }
      }, this.schema.items.enum.map(value =>
        h('option', { value }, value)  
      ));
    } else if (this.schema.type === 'boolean') {
      return h('div', [
        h('input', {
          type: 'checkbox',
          value: 'true',
          checked: this.schema.default || false,
          onChange: event => {
            this.schema.default = event.target.value;
            this.$emit('update:schema', this.schema); 
          }
        }),
        'True',
        h('input', {
          type: 'radio', 
          value: 'false',
          checked: this.schema.default === false,
          onChange: () => {
            this.schema.default = false;
            this.$emit('update:schema', this.schema);
          }
        }),
        'False'
      ]);
    } else {
      return h('input', {
        value: this.schema.default,
        onInput: event => {
          this.schema.default = event.target.value;
          this.$emit('update:schema', this.schema);
        },
        type: 'text' 
      });
    }
  }
};

</script>