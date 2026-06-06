<template>
  <div class="quality-status-selector">
    <button
      v-for="option in options"
      :key="option.value"
      :class="[
        'status-btn',
        { active: modelValue === option.value },
        option.value
      ]"
      @click="handleSelect(option.value)"
    >
      <span class="status-icon">{{ option.icon }}</span>
      <span class="status-text">{{ option.label }}</span>
    </button>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: '合格'
  }
});

const emit = defineEmits(['update:modelValue']);

const options = [
  { value: '合格', label: '合格', icon: '✓' },
  { value: '不合格', label: '不合格', icon: '✗' }
];

function handleSelect(value) {
  emit('update:modelValue', value);
}
</script>

<style scoped>
.quality-status-selector {
  display: flex;
  gap: 8px;
}

.status-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
}

.status-btn:hover {
  border-color: #409eff;
}

.status-btn.active {
  color: #fff;
  border-color: transparent;
}

.status-btn.合格.active {
  background: #67c23a;
}

.status-btn.不合格.active {
  background: #f56c6c;
}

.status-btn.合格:not(.active):hover {
  background: #f0f9eb;
}

.status-btn.不合格:not(.active):hover {
  background: #fef0f0;
}

.status-icon {
  font-size: 14px;
  font-weight: bold;
}

.status-text {
  font-weight: 500;
}
</style>