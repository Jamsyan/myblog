<script setup>
import { ref } from 'vue';
import { createPost, updatePost } from '../services';

const props = defineProps({
  post: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['save', 'cancel']);

const title = ref(props.post?.title || '');
const summary = ref(props.post?.summary || '');
const content = ref(props.post?.content || '');
const status = ref(props.post?.status || 'draft');

const handleSave = async () => {
  const postData = {
    title: title.value,
    summary: summary.value,
    content: content.value,
    status: status.value
  };

  try {
    if (props.post) {
      await updatePost(props.post.id, postData);
    } else {
      await createPost(postData);
    }
    emit('save', postData);
  } catch (error) {
    console.error('Failed to save post:', error);
  }
};

const handleCancel = () => {
  emit('cancel');
};
</script>

<template>
  <div class="post-editor">
    <div class="editor-header">
      <h2>{{ post ? '编辑帖子' : '创建新帖子' }}</h2>
      <div class="editor-actions">
        <button class="btn-secondary" @click="handleCancel">取消</button>
        <button class="btn-primary" @click="handleSave">保存</button>
      </div>
    </div>

    <div class="editor-form">
      <div class="form-group">
        <label>标题</label>
        <input
          v-model="title"
          type="text"
          class="form-input"
          placeholder="输入帖子标题..."
        />
      </div>

      <div class="form-group">
        <label>摘要</label>
        <textarea
          v-model="summary"
          class="form-textarea"
          placeholder="输入帖子摘要..."
          rows="3"
        ></textarea>
      </div>

      <div class="form-group">
        <label>内容</label>
        <textarea
          v-model="content"
          class="form-textarea content-editor"
          placeholder="输入帖子内容..."
          rows="15"
        ></textarea>
      </div>

      <div class="form-group">
        <label>状态</label>
        <div class="status-selector">
          <button
            :class="['status-btn', { active: status === 'draft' }]"
            @click="status = 'draft'"
          >
            草稿
          </button>
          <button
            :class="['status-btn', { active: status === 'published' }]"
            @click="status = 'published'"
          >
            发布
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-editor {
  background: var(--card-background);
  backdrop-filter: blur(10px);
  border-radius: var(--border-radius-lg);
  padding: 32px;
  box-shadow: var(--shadow-lg);
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.editor-header h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.editor-actions {
  display: flex;
  gap: 12px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 24px;
  border: none;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-button-hover);
}

.btn-secondary {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: var(--background-primary);
  color: var(--text-primary);
  font-size: 1rem;
  font-family: var(--font-family-sans);
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(198, 40, 40, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.content-editor {
  min-height: 300px;
  line-height: 1.6;
}

.status-selector {
  display: flex;
  gap: 12px;
}

.status-btn {
  padding: 10px 24px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-md);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
}

.status-btn:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.status-btn.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

@media (max-width: 768px) {
  .post-editor {
    padding: 24px;
  }

  .editor-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .editor-actions {
    width: 100%;
  }

  .btn-primary,
  .btn-secondary {
    flex: 1;
  }
}
</style>