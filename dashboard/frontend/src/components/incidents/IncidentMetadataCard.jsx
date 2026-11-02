import ElapsedTime from '../common/ElapsedTime'

const Row = ({ label, children, mono = true }) => (
  <div className="flex items-center justify-between gap-4 text-xs sm:text-sm">
    <span className="font-medium text-slate-400">{label}</span>
    <span className={`text-right font-medium text-slate-200 ${mono ? 'font-mono text-xs' : ''}`}>
      {children}
    </span>
  </div>
)

function assigneeLabel(approval) {
  if (!approval) return 'No approval yet'
  if (approval.status === 'pending') return 'Awaiting decision'
  return approval.actioned_by || '—'
}

const IncidentMetadataCard = ({ incident }) => {
  const approval = incident.approval_requests?.at(-1)

  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
      <div className="absolute inset-y-0 left-0 w-[3px] bg-emerald-500" />
      <div className="space-y-4">
        <Row label="Namespace">{incident.namespace}</Row>
        <Row label="Service">{incident.service}</Row>
        <Row label="Severity">{incident.severity}</Row>
        <Row label="Duration">
          <ElapsedTime start={incident.created_at} end={incident.resolved_at} />
        </Row>
        <Row label="Decided by">{assigneeLabel(approval)}</Row>
      </div>
    </div>
  )
}

export default IncidentMetadataCard