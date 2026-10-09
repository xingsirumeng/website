// 与后端 app/schemas.py 一一对应的类型定义。
// 注意：项目开了 verbatimModuleSyntax，引用这些类型必须写 `import type`，
// 否则 vue-tsc 会保留 import 语句，打包时报 “xxx is not exported”。

export interface PostSummary {
  id: number
  title: string
  summary: string
  tags: string[]
  published: boolean
  created_at: string
  updated_at: string
}

export interface PostDetail extends PostSummary {
  content: string
}

export interface TagCount {
  name: string
  count: number
}

export interface Project {
  id: number
  name: string
  description: string
  /** 技术栈，逗号分隔的字符串（后端不拆成数组，前端展示时再分） */
  tech: string
  demo_url: string
  repo_url: string
  /** 封面：本站 /images/ 下的相对地址，或外链 */
  cover: string
  /** 排序权重，越大越靠前 */
  sort: number
  published: boolean
  created_at: string
}

export interface Todo {
  id: number
  text: string
  done: boolean
  created_at: string
}
