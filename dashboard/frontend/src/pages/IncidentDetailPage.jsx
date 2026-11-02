import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import StatusBadge from '../components/common/StatusBadge'
import LiveClock from '../components/common/LiveClock'
import IncidentMetadataCard from '../components/incidents/IncidentMetadataCard'
import IncidentRecentLogsCard from '../components/incidents/IncidentRecentLogsCard'
import IncidentWorkflowSteps from '../components/incidents/IncidentWorkflowSteps'
import { useIncident, useIncidentActions } from '../api/queries'
import { getIncidentStatus } from '../constants/status'

const BackLink = () => (
  <Link
    to="/incidents"
    className="group mb-2 inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 transition-colors hover:text-white"
  >
    <ArrowLeft className="h-3.5 w-3.5 transition-transform group-hover:-translate-x-0.5" />
    <span>Back to incidents</span>
  </Link>
)

const IncidentDetailPage = () => {
  const { id } = useParams()
  const { data: incident, error, isPending } = useIncident(id)
  const { approve, reject, notify } = useIncidentActions(id)
  const [rejectReason, setRejectReason] = useState(null) // null = form closed

  if (isPending) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">
        Loading incident #{id}...
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-4">
        <BackLink />
        <div className="rounded-lg border border-red-800 bg-red-950/60 p-4 text-sm text-red-200">
          {error.status === 404 ? 'Incident not found' : `Failed to load incident: ${error.message}`}
        </div>
      </div>
    )
  }

  const actionError = approve.error || reject.error || notify.error
  const actionLoading = approve.isPending || reject.isPending
  const lastApproval = incident.approval_requests.at(-1)

  const submitReject = (e) => {
    e.preventDefault()
    const reason = rejectReason.trim()
    if (!reason) return
    reject.mutate(reason, { onSuccess: () => setRejectReason(null) })
  }

  return (
    <div className="space-y-6">
      <div>
        <BackLink />
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white sm:text-2xl">
              {incident.service}
              <span className="font-normal text-slate-400"> — </span>
              {incident.title}
            </h1>
            <p className="mt-1 font-mono text-xs text-slate-400 sm:text-sm">
              {incident.namespace}
              <span className="mx-2 text-slate-600">·</span>
              <span>incident #{incident.id}</span>
              <span className="mx-2 text-slate-600">·</span>
              <span className="font-semibold uppercase text-amber-400">{incident.severity}</span>
            </p>
          </div>
          <div className="flex items-center gap-3 sm:self-start">
            <StatusBadge {...getIncidentStatus(incident.status)} />
            <LiveClock className="text-sm text-slate-500" />
          </div>
        </div>
      </div>

      {actionError && (
        <div className="rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
          {actionError.message}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        <div className="space-y-4 lg:col-span-4">
          <IncidentMetadataCard incident={incident} />
          <IncidentRecentLogsCard />
        </div>

        <div className="lg:col-span-8">
          <IncidentWorkflowSteps
            incident={incident}
            onApprove={() => approve.mutate()}
            onReject={() => setRejectReason('')}
            onNotifySlack={() => notify.mutate(Boolean(lastApproval?.slack_message_ts))}
            actionLoading={actionLoading}
            notifyLoading={notify.isPending}
          />

          {rejectReason !== null && (
            <form onSubmit={submitReject} className="mt-3 flex flex-wrap gap-2">
              <input
                autoFocus
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Reason for rejection"
                maxLength={2000}
                className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-rose-500"
              />
              <button
                type="submit"
                disabled={!rejectReason.trim() || reject.isPending}
                className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-500 disabled:opacity-40"
              >
                Confirm reject
              </button>
              <button
                type="button"
                onClick={() => setRejectReason(null)}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
              >
                Cancel
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

export default IncidentDetailPage