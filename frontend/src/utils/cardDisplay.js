/**
 * Human-readable ids: T-12 (task), N-5 (note).
 * Dates: short RU locale (dd.mm.yyyy).
 */

export function formatCardCode(type, number) {
  if (number == null || number === '') {
    return type === 'note' ? 'N-?' : 'T-?'
  }
  const prefix = type === 'note' ? 'N' : 'T'
  return `${prefix}-${number}`
}

export function formatCreatedAtRu(value) {
  if (!value) {
    return '—'
  }
  const date = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(date.getTime())) {
    return '—'
  }
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

export function formatCardMetaLine(type, data) {
  const code = formatCardCode(type, data?.number)
  const date = formatCreatedAtRu(data?.created_at)
  return `${code} · ${date}`
}

export function formatCardCanvasText(type, data) {
  const title = data?.title || 'Без названия'
  return `${formatCardMetaLine(type, data)}\n${title}`
}

/** Single-line label for selects and journal rows: meta + title. */
export function formatCardListLine(type, data) {
  const title = data?.title || 'Без названия'
  return `${formatCardMetaLine(type, data)} — ${title}`
}

export function isDarkTheme() {
  return document.documentElement.getAttribute('data-theme') === 'dark'
}

export function cardThemeColors(type) {
  const dark = isDarkTheme()
  if (type === 'note') {
    return dark
      ? { fill: '#422006', stroke: '#f59e0b', titleFill: '#fef3c7', metaFill: '#fcd34d' }
      : { fill: '#fef9c3', stroke: '#ea580c', titleFill: '#1c1917', metaFill: '#78716c' }
  }
  return dark
    ? { fill: '#1e3a5f', stroke: '#60a5fa', titleFill: '#e0f2fe', metaFill: '#93c5fd' }
    : { fill: '#dbeafe', stroke: '#2563eb', titleFill: '#0f172a', metaFill: '#64748b' }
}
