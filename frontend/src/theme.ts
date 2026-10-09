import type { GlobalThemeOverrides } from 'naive-ui'

/**
 * Naive UI 的主题覆盖。
 *
 * 两个后台页面（文章管理、项目管理）以及它们弹出来的 message / dialog 都要用同一份，
 * 所以集中在这里，避免改一处漏一处导致提示框还是蓝色的。
 *
 * 这里只 import type，编译后不会有运行时代码，不会把 Naive UI 拖进公开页面的 bundle。
 */
export const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#42b883',
    primaryColorHover: '#4fd39a',
    primaryColorPressed: '#369d6f',
    primaryColorSuppl: '#4fd39a',
    borderRadius: '6px',
    fontFamily:
      "system-ui, -apple-system, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif",
  },
}
