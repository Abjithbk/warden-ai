import { useNow } from '../../hooks/useNow'
import { formatDuration, parseApiDate } from '../../utils/format'

// Ticks every second only while the incident is still open.
const ElapsedTime = ({ start, end }) => {
    const now = useNow(end ? 60_000 : 1000)
    const startMs = parseApiDate(start)?.getTime()
    if (!startMs) return '—'
    const endMs = end ? parseApiDate(end).getTime() : now
    return <>{formatDuration((endMs - startMs) / 1000)}</>
}

export default ElapsedTime