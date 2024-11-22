<!-- Configure.vue -->
<template>
  <div class="recursive-form">
    <RecursiveForm
      :schema="localSchema"
      :depth="0"
      @update:modelValue="handleSchemaUpdate"
    />
  </div>
</template>

<script setup>
import { ref, h, watch } from 'vue';

const props = defineProps({
  schema: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update:schema']);

// Create a deep copy of the schema to avoid direct mutations
const localSchema = ref(JSON.parse(JSON.stringify(props.schema)));

// Watch for external schema changes
watch(() => props.schema, (newSchema) => {
  localSchema.value = JSON.parse(JSON.stringify(newSchema));
}, { deep: true });
// Emit the updated schema to the parent component
const handleSchemaUpdate = (newValue) => {
  localSchema.value = newValue;
  emit('update:schema', newValue);
};

// Extracted RecursiveForm component
const RecursiveForm = {
  name: 'RecursiveForm',
  props: {
    schema: {
      type: Object,
      required: true
    },
    depth: {
      type: Number,
      default: 0
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const updateSchema = (newValue) => {
      emit('update:modelValue', newValue);
    };

    return {
      updateSchema
    };
  },
  render() {
    const updateNestedSchema = (key, value, schema) => {
      const newSchema = JSON.parse(JSON.stringify(schema));
      if (schema.type === 'object') {
        newSchema.properties[key] = value;
      } else {
        newSchema.default = value;
      }
      this.updateSchema(newSchema);
    };

    const renderObjectType = () => {
      return h('details', {
        class: 'schema-object'
      }, [
        h('summary', { class: 'schema-summary' }, this.schema.repr_name || 'Object'),
        h('div', {
          class: 'schema-properties',
          style: { marginLeft: `${this.depth * 20}px` }
        }, 
        Object.entries(this.schema.properties).map(([key, subSchema]) => 
          h('div', { class: 'property-item' }, [
            h('label', { class: 'property-label' }, key),
            h(RecursiveForm, {
              schema: subSchema,
              depth: this.depth + 1,
              'onUpdate:modelValue': (value) => updateNestedSchema(key, value, this.schema)
            })
          ])
        ))
      ]);
    };

    const renderArrayType = () => {
      return h('select', {
        value: this.schema.default,
        onChange: (event) => {
          const newSchema = { ...this.schema, default: event.target.value };
          this.updateSchema(newSchema);
        },
        class: 'schema-select'
      }, this.schema.items.enum.map(value =>
        h('option', { value }, value)
      ));
    };

    const renderBooleanType = () => {
      return h('div', { class: 'boolean-group' }, [
        h('label', { class: 'boolean-option' }, [
          h('input', {
            type: 'radio',
            checked: this.schema.default === true,
            onChange: () => {
              const newSchema = { ...this.schema, default: true };
              this.updateSchema(newSchema);
            }
          }),
          ' True'
        ]),
        h('label', { class: 'boolean-option' }, [
          h('input', {
            type: 'radio',
            checked: this.schema.default === false,
            onChange: () => {
              const newSchema = { ...this.schema, default: false };
              this.updateSchema(newSchema);
            }
          }),
          ' False'
        ])
      ]);
    };

    const renderDefaultInput = () => {
      const inputType = this.schema.type === 'number' ? 'number' : 'text';
      return h('input', {
        type: inputType,
        value: this.schema.default,
        onInput: (event) => {
          const value = inputType === 'number' ? Number(event.target.value) : event.target.value;
          const newSchema = { ...this.schema, default: value };
          this.updateSchema(newSchema);
        },
        class: 'schema-input'
      });
    };

    // Main render logic
    switch (this.schema.type) {
      case 'object':
        return renderObjectType();
      case 'array':
        return renderArrayType();
      case 'boolean':
        return renderBooleanType();
      default:
        return renderDefaultInput();
    }
  }
};
</script>

<style scoped>
.recursive-form {
  font-family: sans-serif;
}

.schema-object {
  margin: 8px 0;
}

.schema-summary {
  font-weight: bold;
  cursor: pointer;
}

.schema-properties {
  padding: 8px 0;
}

.property-item {
  margin: 8px 0;
}

.property-label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
}

.schema-select,
.schema-input {
  padding: 4px 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 200px;
}

.boolean-group {
  display: flex;
  gap: 16px;
}

.boolean-option {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>