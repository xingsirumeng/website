// 后端返回的是东八区的 ISO 字符串（不带时区标记）。
// 直接截取字符，不要用 new Date() 解析 —— 那会按浏览器所在时区重新解释，读者在国外会看到错日期。
export function formatDate(iso: string): string {
  return iso.slice(0, 10)
}

// '2026-09' → '2026 年 9 月'
export function formatMonth(key: string): string {
  const [year, month] = key.split('-')
  return `${year} 年 ${Number(month)} 月`
}
