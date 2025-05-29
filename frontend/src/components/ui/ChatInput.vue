<template>
  <div class="chat-input-container">
    <!-- 主输入区域 -->
    <div class="input-main-area">
      <!-- 表情和功能按钮 -->
      <div class="input-controls left">
        <NeonButton
          size="small"
          variant="ghost"
          icon="fas fa-smile"
          @click="toggleEmojiPicker"
          :disabled="disabled"
          title="表情符号"
        />
      </div>
      
      <!-- 输入框区域 -->
      <div :class="['input-wrapper', { 'input-focused': isFocused, 'input-disabled': disabled }]">
        <!-- 文本输入区域 -->
        <div class="input-content">
          <textarea
            ref="textareaRef"
            v-model="inputValue"
            :placeholder="placeholder"
            :disabled="disabled"
            :maxlength="maxLength"
            class="chat-textarea"
            @focus="onFocus"
            @blur="onBlur"
            @keydown="onKeyDown"
            @input="onInput"
          ></textarea>
          
          <!-- 字符计数 -->
          <div v-if="showCharCount" class="char-count">
            {{ inputValue.length }} / {{ maxLength }}
          </div>
        </div>
      </div>
      
      <!-- 发送按钮 -->
      <div class="send-button-area">
        <NeonButton
          variant="primary"
          size="small"
          icon="fas fa-paper-plane"
          :loading="sending"
          :disabled="disabled || !canSend"
          @click="sendMessage"
          title="发送消息 (Ctrl+Enter)"
        >
          发送
        </NeonButton>
      </div>
    </div>
   
    <!-- 表情选择器 -->
    <Transition name="emoji-picker">
      <div v-if="showEmojiPicker" class="emoji-picker">
        <div class="emoji-header">
          <span class="emoji-title">选择表情</span>
          <button class="emoji-close" @click="closeEmojiPicker">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="emoji-grid">
          <button
            v-for="emoji in emojiList"
            :key="emoji"
            class="emoji-item"
            @click="insertEmoji(emoji)"
          >
            {{ emoji }}
          </button>
        </div>
      </div>
    </Transition>

    <!-- 提示信息 -->
    <div v-if="hint" class="input-hint">
      <i class="fas fa-info-circle"></i>
      {{ hint }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import NeonButton from './NeonButton.vue'

interface Props {
  placeholder?: string
  disabled?: boolean
  sending?: boolean
  maxLength?: number
  showCharCount?: boolean
  showFileUpload?: boolean
  acceptedFileTypes?: string
  hint?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '输入消息...',
  disabled: false,
  sending: false,
  maxLength: 500,
  showCharCount: true,
  showFileUpload: true,
  acceptedFileTypes: 'image/*,text/*,.pdf,.doc,.docx',
  hint: ''
})

const emit = defineEmits<{
  send: [message: string]
  fileUpload: [file: File]
  typing: []
  stopTyping: []
}>()

// 响应式数据
const inputValue = ref('')
const isFocused = ref(false)
const showEmojiPicker = ref(false)
const textareaRef = ref<HTMLTextAreaElement>()
const fileInputRef = ref<HTMLInputElement>()

// 表情列表
const emojiList = [
  '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣',
  '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰',
  '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜',
  '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏',
  '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣',
  '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠',
  '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨',
  '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙',
  '👏', '🙌', '👐', '🤲', '🤝', '🙏', '💪', '🦾'
]

// 计算属性
const canSend = computed(() => {
  return inputValue.value.trim().length > 0 && !props.sending
})

// 监听输入变化
let typingTimer: number | null = null
watch(inputValue, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    emit('typing')
    
    // 清除之前的计时器
    if (typingTimer) {
      clearTimeout(typingTimer)
    }
    
    // 设置新的计时器，1秒后发送停止输入事件
    typingTimer = setTimeout(() => {
      emit('stopTyping')
    }, 1000)
  }
})

// 事件处理
const onFocus = () => {
  isFocused.value = true
}

const onBlur = () => {
  isFocused.value = false
}

const onInput = () => {
  // 自动调整textarea高度
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    // 设置最小高度为1.5rem，最大高度为120px
    const scrollHeight = textareaRef.value.scrollHeight
    const minHeight = 24 // 约1.5rem
    const maxHeight = 120 // 120px
    const newHeight = Math.min(Math.max(scrollHeight, minHeight), maxHeight)
    textareaRef.value.style.height = newHeight + 'px'
  }
}

const onKeyDown = (event: KeyboardEvent) => {
  // Ctrl+Enter 发送消息
  if (event.key === 'Enter' && event.ctrlKey) {
    event.preventDefault()
    sendMessage()
  }
  // Escape 关闭表情选择器
  else if (event.key === 'Escape' && showEmojiPicker.value) {
    closeEmojiPicker()
  }
}

const sendMessage = () => {
  if (canSend.value) {
    const message = inputValue.value.trim()
    if (message) {
      emit('send', message)
      inputValue.value = ''
      
      // 重置textarea高度
      if (textareaRef.value) {
        textareaRef.value.style.height = 'auto'
      }
    }
  }
}

const toggleEmojiPicker = () => {
  showEmojiPicker.value = !showEmojiPicker.value
}

const closeEmojiPicker = () => {
  showEmojiPicker.value = false
}

const insertEmoji = (emoji: string) => {
  const textarea = textareaRef.value
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const before = inputValue.value.substring(0, start)
    const after = inputValue.value.substring(end)
    
    inputValue.value = before + emoji + after
    
    // 恢复光标位置
    nextTick(() => {
      const newPos = start + emoji.length
      textarea.setSelectionRange(newPos, newPos)
      textarea.focus()
    })
  }
  
  closeEmojiPicker()
}

const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const onFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    emit('fileUpload', file)
    // 清空文件输入
    target.value = ''
  }
}

// 导出方法供父组件调用
defineExpose({
  focus: () => textareaRef.value?.focus(),
  clear: () => {
    inputValue.value = ''
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
})
</script>

<style scoped>
.chat-input-container {
  position: relative;
  width: 100%;
  max-width: 100%;
}

.input-main-area {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 2rem;
  padding: 0.75rem 1rem;
  gap: 0.75rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  width: 100%;
  min-height: 2.75rem;
}

.input-main-area:hover {
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
}

.input-wrapper {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
}

.input-focused .input-main-area {
  border-color: rgba(99, 179, 237, 0.6);
  box-shadow: 0 4px 20px rgba(99, 179, 237, 0.3);
}

.input-disabled .input-main-area {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-controls {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
  width: auto;
  min-width: 2.5rem;
}

.input-content {
  flex: 1;
  position: relative;
  width: 100%;
  min-width: 0;
}

.send-button-area {
  flex-shrink: 0;
  width: auto;
  min-width: 4rem;
}

.chat-textarea {
  width: 100%;
  min-height: 1.5rem;
  max-height: 120px;
  border: none;
  outline: none;
  background: transparent;
  resize: none;
  font-size: 1rem;
  line-height: 1.4;
  color: #e2e8f0;
  font-family: inherit;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(99, 179, 237, 0.3) transparent;
  box-sizing: border-box;
  padding: 0;
}

.chat-textarea::placeholder {
  color: #a0aec0;
}

.chat-textarea::-webkit-scrollbar {
  width: 4px;
}

.chat-textarea::-webkit-scrollbar-track {
  background: transparent;
}

.chat-textarea::-webkit-scrollbar-thumb {
  background: rgba(99, 179, 237, 0.3);
  border-radius: 2px;
}

.char-count {
  position: absolute;
  bottom: -1.5rem;
  right: 0;
  font-size: 0.7rem;
  color: #a0aec0;
  white-space: nowrap;
}

/* 表情选择器 */
.emoji-picker {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: rgba(45, 55, 72, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  margin-bottom: 0.5rem;
}

.emoji-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.emoji-title {
  font-weight: 600;
  color: #e2e8f0;
}

.emoji-close {
  background: none;
  border: none;
  font-size: 1rem;
  color: #a0aec0;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease;
}

.emoji-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.5rem;
  padding: 1rem;
  max-height: 200px;
  overflow-y: auto;
}

.emoji-item {
  background: none;
  border: none;
  font-size: 1.2rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.emoji-item:hover {
  background: rgba(99, 179, 237, 0.2);
  transform: scale(1.1);
}

/* 文件上传 */
.file-input {
  display: none;
}

/* 提示信息 */
.input-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  font-size: 0.8rem;
  color: #a0aec0;
}

/* 动画 */
.emoji-picker-enter-active,
.emoji-picker-leave-active {
  transition: all 0.3s ease;
}

.emoji-picker-enter-from {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

.emoji-picker-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .input-main-area {
    padding: 0.5rem 0.75rem;
    gap: 0.5rem;
    min-height: 2.5rem;
  }
  
  .input-controls {
    min-width: 2rem;
  }
  
  .send-button-area {
    min-width: 3.5rem;
  }
  
  .chat-textarea {
    font-size: 0.9rem;
    min-height: 1.25rem;
    line-height: 1.3;
  }
  
  .emoji-grid {
    grid-template-columns: repeat(6, 1fr);
  }
  
  .emoji-item {
    font-size: 1rem;
    padding: 0.4rem;
  }
}

@media (max-width: 480px) {
  .input-main-area {
    padding: 0.4rem 0.6rem;
    gap: 0.4rem;
    min-height: 2.25rem;
  }
  
  .input-controls {
    min-width: 1.8rem;
  }
  
  .send-button-area {
    min-width: 3rem;
  }
  
  .chat-textarea {
    font-size: 0.85rem;
    min-height: 1rem;
    line-height: 1.2;
  }
}

/* 大屏幕优化 */
@media (min-width: 1024px) {
  .input-main-area {
    padding: 0.875rem 1.25rem;
    gap: 1rem;
    min-height: 3rem;
  }
  
  .input-controls {
    min-width: 3rem;
  }
  
  .send-button-area {
    min-width: 5rem;
  }
  
  .chat-textarea {
    font-size: 1rem;
    min-height: 1.75rem;
    line-height: 1.5;
  }
}
</style> 