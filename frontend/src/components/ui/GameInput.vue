<template>
  <div
    :class="[
      'game-input-container',
      {
        'focused': isFocused,
        'error': hasError,
        'disabled': disabled
      }
    ]"
  >
    <!-- 输入框wrapper -->
    <div class="input-wrapper">
      <!-- 前置图标 -->
      <div v-if="prefixIcon" class="input-prefix">
        <i :class="prefixIcon"></i>
      </div>
      
      <!-- 输入框 -->
      <input
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :maxlength="maxlength"
        class="game-input"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      
      <!-- 后置图标 -->
      <div v-if="suffixIcon || clearable" class="input-suffix">
        <button
          v-if="clearable && modelValue && !disabled"
          @click="handleClear"
          class="clear-btn"
          type="button"
        >
          <i class="fas fa-times"></i>
        </button>
        <i v-if="suffixIcon" :class="suffixIcon"></i>
      </div>
    </div>
    
    <!-- 发光效果 -->
    <div class="input-glow"></div>
    
    <!-- 错误信息 -->
    <div v-if="hasError && errorMessage" class="error-message">
      <i class="fas fa-exclamation-circle"></i>
      <span>{{ errorMessage }}</span>
    </div>
    
    <!-- 字符计数 -->
    <div v-if="showCount && maxlength" class="char-count">
      {{ modelValue?.length || 0 }} / {{ maxlength }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

interface Props {
  modelValue?: string;
  type?: 'text' | 'password' | 'email' | 'number';
  placeholder?: string;
  disabled?: boolean;
  readonly?: boolean;
  clearable?: boolean;
  showCount?: boolean;
  maxlength?: number;
  prefixIcon?: string;
  suffixIcon?: string;
  errorMessage?: string;
  validateOnInput?: boolean;
  validator?: (value: string) => boolean | string;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  placeholder: '',
  disabled: false,
  readonly: false,
  clearable: false,
  showCount: false,
  validateOnInput: false
});

const emit = defineEmits<{
  'update:modelValue': [value: string];
  'focus': [event: FocusEvent];
  'blur': [event: FocusEvent];
  'clear': [];
  'enter': [value: string];
  'validate': [valid: boolean, message?: string];
}>();

const inputRef = ref<HTMLInputElement>();
const isFocused = ref(false);
const validationError = ref<string>('');

const hasError = computed(() => {
  return !!props.errorMessage || !!validationError.value;
});

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const value = target.value;
  
  emit('update:modelValue', value);
  
  if (props.validateOnInput && props.validator) {
    validateInput(value);
  }
};

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true;
  emit('focus', event);
};

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false;
  emit('blur', event);
  
  if (props.validator) {
    validateInput(props.modelValue || '');
  }
};

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter') {
    emit('enter', props.modelValue || '');
  }
};

const handleClear = () => {
  emit('update:modelValue', '');
  emit('clear');
  inputRef.value?.focus();
};

const validateInput = (value: string) => {
  if (!props.validator) return;
  
  const result = props.validator(value);
  
  if (typeof result === 'boolean') {
    validationError.value = result ? '' : '输入值无效';
    emit('validate', result);
  } else {
    validationError.value = result === '' ? '' : result;
    emit('validate', result === '', result === '' ? undefined : result);
  }
};

// 暴露方法
const focus = () => {
  inputRef.value?.focus();
};

const blur = () => {
  inputRef.value?.blur();
};

defineExpose({
  focus,
  blur
});
</script>

<style scoped>
.game-input-container {
  position: relative;
  width: 100%;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  overflow: hidden;
}

.game-input {
  flex: 1;
  padding: 12px 16px;
  background: transparent;
  border: none;
  outline: none;
  color: #ffffff;
  font-size: 14px;
  font-family: inherit;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.game-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
  transition: color 0.3s ease;
}

.input-prefix,
.input-suffix {
  display: flex;
  align-items: center;
  padding: 0 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.input-prefix {
  padding-right: 8px;
}

.input-suffix {
  padding-left: 8px;
}

.clear-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
}

.clear-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.1);
}

/* 发光效果 */
.input-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  border-radius: inherit;
  opacity: 0;
  background: linear-gradient(
    45deg,
    rgba(0, 212, 255, 0.2),
    rgba(255, 0, 150, 0.2)
  );
  transition: opacity 0.3s ease;
  pointer-events: none;
}

/* 聚焦状态 */
.game-input-container.focused .input-wrapper {
  border-color: #00d4ff;
  background: rgba(0, 212, 255, 0.1);
  box-shadow: 
    0 0 20px rgba(0, 212, 255, 0.3),
    0 4px 15px rgba(0, 0, 0, 0.2);
  transform: translateY(-1px);
}

.game-input-container.focused .input-glow {
  opacity: 1;
  animation: glow-pulse 2s ease-in-out infinite;
}

.game-input-container.focused .game-input::placeholder {
  color: rgba(255, 255, 255, 0.8);
}

/* 错误状态 */
.game-input-container.error .input-wrapper {
  border-color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
  box-shadow: 
    0 0 15px rgba(231, 76, 60, 0.3),
    0 4px 15px rgba(0, 0, 0, 0.2);
}

.game-input-container.error .input-glow {
  background: linear-gradient(
    45deg,
    rgba(231, 76, 60, 0.2),
    rgba(255, 107, 107, 0.2)
  );
  opacity: 1;
}

/* 禁用状态 */
.game-input-container.disabled .input-wrapper {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.05);
}

.game-input-container.disabled .game-input {
  cursor: not-allowed;
}

/* 错误信息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: 6px;
  color: #ff6b6b;
  font-size: 12px;
  font-weight: 500;
}

/* 字符计数 */
.char-count {
  text-align: right;
  margin-top: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

/* 动画 */
@keyframes glow-pulse {
  0%, 100% {
    opacity: 0.3;
  }
  50% {
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .game-input {
    padding: 10px 14px;
    font-size: 13px;
  }
  
  .input-prefix,
  .input-suffix {
    padding: 0 10px;
    font-size: 13px;
  }
}

/* 深色主题适配 */
.dark .input-wrapper {
  background: rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .game-input {
  color: #ffffff;
}

.dark .game-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.dark .game-input-container.focused .input-wrapper {
  background: rgba(0, 212, 255, 0.15);
}

/* 自动填充样式修正 */
.game-input:-webkit-autofill,
.game-input:-webkit-autofill:hover,
.game-input:-webkit-autofill:focus {
  -webkit-box-shadow: 0 0 0px 1000px rgba(0, 212, 255, 0.1) inset;
  -webkit-text-fill-color: #ffffff;
  transition: background-color 5000s ease-in-out 0s;
}
</style> 