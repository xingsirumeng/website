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
