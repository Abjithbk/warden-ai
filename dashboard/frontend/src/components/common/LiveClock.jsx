import { useNow } from '../../hooks/useNow'

const LiveClock = ({ className = '' }) => (
    <span className={`font-mono tabular-nums ${className}`}>
        {new Date(useNow()).toLocaleTimeString('en-GB')}
    </span>
)

export default LiveClock