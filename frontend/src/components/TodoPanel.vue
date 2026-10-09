<script setup lang="ts">
import { ref, nextTick, watch, onBeforeUnmount } from 'vue'
import {
  AddOutline,
  CloseOutline,
  CreateOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import api from '@/api'
import type { Todo } from '@/types'

// 这个组件挂在公开页面上，所以全部用原生标签手写、不引 Naive UI ——
// 引组件库等于把它那几十 KB 推给每一个读者（哪怕是根本不点开清单的访客）
const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: [] }>()

const todos = ref<Todo[]>([])
const draft = ref('')
const loading = ref(false)
const error = ref('')

// 首次打开时才拉数据。它本来就是懒加载的组件，没必要一挂载就发请求
let loaded = false

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get<Todo[]>('/api/admin/todos')
    todos.value = data
  } catch (err: any) {
    error.value = '加载失败: ' + err.message
  } finally {
    loading.value = false
  }
}

async function add() {
  const text = draft.value.trim()
  if (!text) return
  error.value = ''
  try {
    await api.post('/api/admin/todos', { text })
    draft.value = ''
    await load()
  } catch (err: any) {
    error.value = '添加失败: ' + err.message
  }
}

// 每次都重新拉一遍列表：切换状态后排序会变（完成的沉到底部），
// 只在本地改会和服务端的顺序对不上
async function toggle(todo: Todo) {
  error.value = ''
  try {
    await api.patch(`/api/admin/todos/${todo.id}`, { done: !todo.done })
    await load()
  } catch (err: any) {
    error.value = '操作失败: ' + err.message
  }
}

async function remove(todo: Todo) {
  error.value = ''
  try {
    await api.delete(`/api/admin/todos/${todo.id}`)
    await load()
  } catch (err: any) {
    error.value = '删除失败: ' + err.message
  }
}

/* ---------- 就地编辑文字 ---------- */
const editingId = ref<number | null>(null)
const editText = ref('')
// 用函数 ref 而不是 ref="xxx"：这个 input 在 v-for 里，
// 普通 ref 会被收集成数组，反而更麻烦
let editInputEl: HTMLInputElement | null = null

function setEditInput(el: any) {
  editInputEl = el as HTMLInputElement | null
}

async function startEdit(todo: Todo) {
  editingId.value = todo.id
  editText.value = todo.text
  // 等 DOM 渲染出 input 之后再聚焦选中
  await nextTick()
  editInputEl?.focus()
  editInputEl?.select()
}

async function commitEdit(todo: Todo) {
  // 回车提交后 input 会被移除，随之触发的 blur 会再调一次这里 —— 挡掉
  if (editingId.value !== todo.id) return

  const text = editText.value.trim()
  editingId.value = null
  // 没改或者改成空的就当作放弃
  if (!text || text === todo.text) return

  error.value = ''
  try {
    await api.patch(`/api/admin/todos/${todo.id}`, { text })
    await load()
  } catch (err: any) {
    error.value = '修改失败: ' + err.message
  }
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') emit('close')
}

watch(
  () => props.open,
  (open) => {
    if (open) {
      window.addEventListener('keydown', onKeydown)
      if (!loaded) {
        loaded = true
        load()
      }
    } else {
      window.removeEventListener('keydown', onKeydown)
    }
  },
)

onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <!-- Teleport 到 body：面板在 App.vue 里是写在 <nav> 内部的，
       不放出来的话会被导航栏的层叠和换行影响 -->
  <Teleport to="body">
    <div class="todo-mask" :class="{ open }" @click="emit('close')"></div>

    <aside class="todo-panel" :class="{ open }" aria-label="待办清单">
      <header class="todo-head">
        <span>清单</span>
        <button class="icon-btn" title="关闭" @click="emit('close')">
          <CloseOutline class="svg-icon" />
        </button>
      </header>

      <div class="todo-add">
        <input
          v-model="draft"
          type="text"
          placeholder="添加一条…"
          maxlength="500"
          @keydown.enter="add"
        />
        <button class="add-btn" :disabled="!draft.trim()" title="添加" @click="add">
          <AddOutline class="svg-icon" />
        </button>
      </div>

      <p v-if="error" class="msg error">{{ error }}</p>
      <p v-else-if="loading" class="msg">加载中…</p>
      <p v-else-if="todos.length === 0" class="msg">还没有条目</p>

      <ul v-else class="todo-list">
        <li v-for="todo in todos" :key="todo.id" :class="{ done: todo.done }">
          <!-- 勾选框独立出来，不再用 <label> 包住文字：
               文字上挂了双击编辑，包在 label 里单击会误触勾选 -->
          <input type="checkbox" :checked="todo.done" @change="toggle(todo)" />

          <input
            v-if="editingId === todo.id"
            :ref="setEditInput"
            v-model="editText"
            class="edit-input"
            maxlength="500"
            @keydown.enter="commitEdit(todo)"
            @keydown.esc="editingId = null"
            @blur="commitEdit(todo)"
          />
          <span v-else class="text" title="双击编辑" @dblclick="startEdit(todo)">
            {{ todo.text }}
          </span>

          <button class="icon-btn edit" title="编辑" @click="startEdit(todo)">
            <CreateOutline class="svg-icon" />
          </button>
          <button class="icon-btn del" title="删除" @click="remove(todo)">
            <TrashOutline class="svg-icon" />
          </button>
        </li>
      </ul>
    </aside>
  </Teleport>
</template>

<style scoped>
.todo-mask {
  position: fixed;
  inset: 0;
  z-index: 100;
  /* 比抽屉那种全屏遮罩淡一些：这块面板只占一角，
     压得太暗会显得整页都被挡住了 */
  background: rgba(0, 0, 0, 0.25);
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.25s, visibility 0.25s;
}
.todo-mask.open {
  opacity: 1;
  visibility: visible;
}

.todo-panel {
  position: fixed;
  /* 挂在导航栏正下方，右对齐到「清单」按钮那一侧 */
  top: var(--nav-height);
  right: 24px;
  z-index: 101;
  width: min(380px, calc(100vw - 32px));
  /* 高度随内容，最多占屏幕六成 */
  max-height: min(62vh, 520px);
  display: flex;
  flex-direction: column;
  /* 浮层必须不透明。页面的 --card 是故意做成半透明的，
     浮在内容之上时会透出下面的东西，看着很脏 */
  background: #1a1c24;
  border: 1px solid var(--border);
  /* 只有下缘是圆角：上缘和导航栏贴在一起，圆角会露出缝隙 */
  border-radius: 0 0 12px 12px;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.5);
  /* 淡入淡出。用 visibility 而不是 display：
     它跟着 opacity 一起过渡，关闭时会等淡出结束才真正隐藏，
     不会中途「啪」地消失。收起状态必须真的隐藏 —— 导航栏是全透明的，
     面板留在那儿会直接透出来。 */
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease, visibility 0.2s;
}
.todo-panel.open {
  opacity: 1;
  visibility: visible;
}
@media (prefers-reduced-motion: reduce) {
  .todo-mask,
  .todo-panel {
    transition: none;
  }
}

.todo-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  font-size: 1rem;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: none;
  border-radius: 6px;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}
.icon-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text);
}

.todo-add {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
}
.todo-add input {
  flex: 1;
  min-width: 0;
  font: inherit;
  font-size: 0.92rem;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text);
  outline: none;
  transition: border-color 0.2s;
}
.todo-add input:focus {
  border-color: var(--brand);
}
.add-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  flex-shrink: 0;
  border: none;
  border-radius: 6px;
  background: var(--brand);
  color: #fff;
  cursor: pointer;
  transition: opacity 0.2s;
}
.add-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.msg {
  margin: 16px;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.msg.error {
  color: var(--danger);
}

.todo-list {
  /* min-height: 0 是关键 —— 不加的话 flex 子项不会收缩，
     列表撑不下时会把整个面板顶出屏幕，而不是自己内部滚动 */
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 6px 0;
}
.todo-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 10px 7px 16px;
}
.todo-list li:hover {
  background: rgba(255, 255, 255, 0.05);
}
.todo-list input[type='checkbox'] {
  flex-shrink: 0;
  width: 16px;
  height: 16px;
  accent-color: var(--brand);
  cursor: pointer;
}
.todo-list .text {
  /* flex: 1 撑满中间，两个按钮才不会被长文字挤走 */
  flex: 1;
  min-width: 0;
  font-size: 0.92rem;
  line-height: 1.5;
  /* 长条目要能换行，不然会溢出面板 */
  overflow-wrap: anywhere;
}
/* 就地编辑时替换文字的那个输入框 */
.edit-input {
  flex: 1;
  min-width: 0;
  font: inherit;
  font-size: 0.92rem;
  padding: 2px 6px;
  border: 1px solid var(--brand);
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
  outline: none;
}
.todo-list li.done .text {
  color: var(--text-muted);
  text-decoration: line-through;
}
/* 编辑和删除按钮平时藏起来，悬停该条目时才出现，让列表看起来干净些 */
.todo-list .edit,
.todo-list .del {
  opacity: 0;
  flex-shrink: 0;
}
.todo-list li:hover .edit,
.todo-list li:hover .del,
.todo-list .edit:focus-visible,
.todo-list .del:focus-visible {
  opacity: 1;
}
.todo-list .edit:hover {
  color: var(--brand);
}
.todo-list .del:hover {
  color: var(--danger);
}
</style>
