import { Link } from 'react-router-dom'
import StatusBadge from './common/StatusBadge'
import { DOT_CLASSES, getIncidentStatus } from '../constants/status'
import { formatTimeAgo } from '../utils/format'

function LiveIncidentFeed({ incidents = [] }) {
  return (
    <div className="rounded-xl border border-gray-800 bg-slate-900 p-5">
      <p className="mb-4 text-xs tracking-wide text-gray-400">LIVE INCIDENT FEED</p>
      {incidents.length === 0 ? (
        <p className="py-4 text-sm text-slate-500">No open incidents. All clear.</p>
      ) : (
        <div className="flex flex-col">
          {incidents.map((incident, index) => {
            const status = getIncidentStatus(incident.status)
            return (
              <Link
                key={incident.id}
                to={`/incidents/${incident.id}`}
                className={`group -mx-2 flex items-center justify-between rounded-lg px-2 py-3 transition-colors hover:bg-slate-800/40 ${index !== incidents.length - 1 ? 'border-b border-gray-800' : ''
                  }`}
              >
                <div className="flex items-start gap-3">
                  <span aria-hidden="true" className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${DOT_CLASSES[status.tone]}`} />
                  <div>
                    <p className="text-sm font-semibold text-white transition-colors group-hover:text-indigo-300">
                      {incident.service} — {incident.title}
                    </p>
                    <p className="mt-0.5 text-xs text-gray-500">
                      namespace: {incident.namespace} · severity: {incident.severity}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge {...status} />
                  <span className="whitespace-nowrap text-xs text-gray-500">{formatTimeAgo(incident.created_at)}</span>
                </div>
              </Link>
            )
          })}
        </div>
      )}
      <Link to="/incidents" className="mt-5 inline-block text-sm text-indigo-400 hover:underline">
        View all incidents →
      </Link>
    </div>
  )
}

export default LiveIncidentFeed