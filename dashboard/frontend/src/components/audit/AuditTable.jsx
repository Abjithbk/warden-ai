import { Link } from 'react-router-dom'
import StatusBadge from '../common/StatusBadge'
import { getAuditAction } from '../../constants/status'
import { formatDateTime, formatIncidentId } from '../../utils/format'

// "slack:U123" -> [slack] U123, "dashboard:operator" -> [dashboard] operator
const ActorCell = ({ actor }) => {
  const [source, ...rest] = (actor || '').split(':')
  const name = rest.join(':')
  if (!name) return <span className="text-sm text-slate-300">{actor || '-'}</span>
  const styles =
    source === 'slack'
      ? 'bg-fuchsia-500/15 text-fuchsia-300 border-fuchsia-500/30'
      : 'bg-slate-500/15 text-slate-300 border-slate-500/30'
  return (
    <span className="inline-flex items-center gap-2 text-sm text-slate-300">
      <span className={`rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider ${styles}`}>
        {source}
      </span>
      {name}
    </span>
  )
}

const extractService = (detail) => detail?.target || detail?.service || detail?.source || '-'
const th = 'px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500'

const AuditTable = ({ entries }) => {
  if (entries.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-8 text-center">
        <p className="text-sm text-slate-400">No results found</p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50">
      <div className="hidden md:block">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className={th}>Time</th>
              <th className={th}>Incident</th>
              <th className={th}>Service</th>
              <th className={th}>Actor</th>
              <th className={th}>Event</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {entries.map((e) => (
              <tr key={e.id} className="transition-colors hover:bg-slate-800/40">
                <td className="px-5 py-3.5 font-mono text-xs text-slate-500">{formatDateTime(e.created_at)}</td>
                <td className="px-5 py-3.5 text-sm font-semibold">
                  <Link to={`/incidents/${e.incident_id}`} className="text-white hover:text-indigo-300">
                    {formatIncidentId(e.incident_id)}
                  </Link>
                </td>
                <td className="px-5 py-3.5 text-sm text-slate-300">{extractService(e.detail)}</td>
                <td className="px-5 py-3.5"><ActorCell actor={e.actor} /></td>
                <td className="px-5 py-3.5"><StatusBadge {...getAuditAction(e.action)} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="divide-y divide-slate-800 md:hidden">
        {entries.map((e) => (
          <div key={e.id} className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <Link to={`/incidents/${e.incident_id}`} className="text-sm font-semibold text-white">
                {formatIncidentId(e.incident_id)}
              </Link>
              <StatusBadge {...getAuditAction(e.action)} />
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Time</span>
                <span className="font-mono text-xs text-slate-400">{formatDateTime(e.created_at)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Service</span>
                <span className="text-slate-300">{extractService(e.detail)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Actor</span>
                <ActorCell actor={e.actor} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default AuditTable