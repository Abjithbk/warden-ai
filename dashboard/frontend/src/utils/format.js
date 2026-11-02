// SQLite returns naive timestamps that are really UTC; force a UTC parse.
export function parseApiDate(value) {
    if (!value) return null
    const hasZone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(value)
    return new Date(hasZone ? value : `${value}Z`)
}

export function formatTimeAgo(value) {
    const date = parseApiDate(value)
    if (!date) return '—'
    const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000))
    if (seconds < 60) return 'just now'
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    return `${Math.floor(hours / 24)}d ago`
}

export function formatDuration(seconds) {
    if (seconds == null || Number.isNaN(seconds)) return '—'
    const s = Math.max(0, Math.round(seconds))
    if (s < 60) return `${s}s`
    const m = Math.floor(s / 60)
    return s % 60 ? `${m}m ${s % 60}s` : `${m}m`
}

export const formatDateTime = (value) => {
    const date = parseApiDate(value)
    return date ? date.toLocaleString('en-GB') : '—'
}

export const formatIncidentId = (id) => `INC-${String(id).padStart(4, '0')}`
export const humanize = (value) => (value || '').replaceAll('_', ' ')