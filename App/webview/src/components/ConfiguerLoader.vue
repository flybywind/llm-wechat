# SchemaLoader.vue
<template>
  <div class="schema-loader">
    <!-- Loading state -->
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <span>配置加载中...</span>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="error-state">
      <p class="error-message">{{ error }}</p>
      <button @click="loadSchema" class="retry-button">
        Retry
      </button>
    </div>

    <!-- Success state -->
    <Configure
      v-else-if="schema"
      :schema="schema"
      @update:schema="handleSchemaUpdate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Configure from './Configure.vue';

const schema = ref(null);
const isLoading = ref(false);
const error = ref(null);

// Function to load schema from backend
const loadSchema = async () => {
  isLoading.value = true;
  error.value = null;
  
  try {
    const response = await fetch('/api/schema'); // Adjust the URL to your API endpoint
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Validate the schema structure
    if (!isValidSchema(data)) {
      throw new Error('Invalid schema format received from server');
    }
    
    schema.value = data;
  } catch (e) {
    console.error('Error loading schema:', e);
    error.value = `Failed to load schema: ${e.message}`;
  } finally {
    isLoading.value = false;
  }
};

// Basic schema validation
const isValidSchema = (schema) => {
  return schema 
    && typeof schema === 'object'
    && schema.type === 'object'
    && schema.properties
    && typeof schema.properties === 'object';
};

// Handle schema updates
const handleSchemaUpdate = async (newSchema) => {
  try {
    // Optional: Save updated schema back to backend
    const response = await fetch('/api/schema', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newSchema),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to save schema: ${response.status}`);
    }
    
    // Update local schema
    schema.value = newSchema;
  } catch (e) {
    console.error('Error saving schema:', e);
    // Handle save error (you might want to show a notification)
  }
};

// Load schema when component mounts
onMounted(() => {
  loadSchema();
});
</script>

<style scoped>
.schema-loader {
  padding: 1rem;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 1rem;
  color: #666;
}

.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error-state {
  padding: 1rem;
  border: 1px solid #dc3545;
  border-radius: 4px;
  background-color: #fff;
}

.error-message {
  color: #dc3545;
  margin-bottom: 1rem;
}

.retry-button {
  padding: 0.5rem 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #2980b9;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>