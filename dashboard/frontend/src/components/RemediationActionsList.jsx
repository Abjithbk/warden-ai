import StatusBadge from './common/StatusBadge'
import { DOT_CLASSES, getActionStatus } from '../constants/status'
import { formatTimeAgo, humanize } from '../utils/format'

function RemediationActionsList({ actions = [] }) {
  return (
    <div className="rounded-xl border border-gray-800 bg-slate-900 p-5">
      <p className="mb-4 text-xs tracking-wide text-gray-400">RECENT REMEDIATION ACTIONS</p>
      {actions.length === 0 ? (
        <p className="py-4 text-sm text-slate-500">No remediation actions yet.</p>
      ) : (
        <div className="flex flex-col">
          {actions.map((action, index) => {
            const status = getActionStatus(action.status)
            return (
              <div
                key={action.id}
                className={`flex items-center justify-between py-3 ${index !== actions.length - 1 ? 'border-b border-gray-800' : ''}`}
              >
                <div className="flex items-start gap-3">
                  <span className={`mt-1.5 h-2 w-2 rounded-full ${DOT_CLASSES[status.tone]}`} />
                  <div>
                    <p className="text-sm font-semibold text-white">
                      {humanize(action.action_type)} on {action.service || action.target}
                    </p>
                    <p className="mt-0.5 text-xs text-gray-500">{action.incident_title}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge {...status} />
                  <span className="whitespace-nowrap text-xs text-gray-500">
                    {formatTimeAgo(action.completed_at || action.started_at)}
                  </span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default RemediationActionsList