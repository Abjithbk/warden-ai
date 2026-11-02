import { Link } from 'react-router-dom'
import StatusBadge from '../common/StatusBadge'
import { BORDER_CLASSES, getIncidentStatus } from '../../constants/status'
import { formatTimeAgo } from '../../utils/format'

const IncidentCard = ({ incident }) => {
  const status = getIncidentStatus(incident.status)

  return (
    <Link
      to={`/incidents/${incident.id}`}
      className={`group flex items-center justify-between rounded-lg border-l-[3px] bg-slate-800/40 px-5 py-4 transition-all duration-200 hover:translate-x-0.5 hover:bg-slate-800/70 ${BORDER_CLASSES[status.tone]}`}
    >
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-white">
          {incident.service}
          <span className="font-normal text-slate-400"> — </span>
          {incident.title}
        </p>
        <p className="mt-1 truncate text-xs text-slate-500">
          {incident.namespace} / {incident.service}
          <span className="mx-1.5 text-slate-600">·</span>
          Severity: {incident.severity}
        </p>
      </div>

      <div className="ml-4 flex shrink-0 flex-col items-end gap-1.5">
        <StatusBadge {...status} />
        <span className="text-[11px] text-slate-500">{formatTimeAgo(incident.created_at)}</span>
      </div>
    </Link>
  )
}

export default IncidentCard