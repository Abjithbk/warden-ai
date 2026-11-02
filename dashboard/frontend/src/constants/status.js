// Tailwind only sees complete class names, so every class is written out in full.
export const TONE_CLASSES = {
    indigo: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
    amber: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
    emerald: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    rose: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
    slate: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
}

export const BORDER_CLASSES = {
    indigo: 'border-l-indigo-500',
    amber: 'border-l-amber-500',
    yellow: 'border-l-yellow-400',
    emerald: 'border-l-emerald-500',
    rose: 'border-l-rose-500',
    slate: 'border-l-slate-500',
}

export const DOT_CLASSES = {
    indigo: 'bg-indigo-400',
    amber: 'bg-amber-400',
    yellow: 'bg-yellow-400',
    emerald: 'bg-emerald-400',
    rose: 'bg-rose-400',
    slate: 'bg-slate-400',
}

export const INCIDENT_STATUS = {
    active: { label: 'Active', tone: 'amber' },
    awaiting_approval: { label: 'Awaiting Approval', tone: 'indigo' },
    remediating: { label: 'Remediating', tone: 'yellow' },
    resolved: { label: 'Resolved', tone: 'emerald' },
    rejected: { label: 'Rejected', tone: 'rose' },
}

export const ACTION_STATUS = {
    pending: { label: 'Pending', tone: 'slate' },
    in_progress: { label: 'In progress', tone: 'amber' },
    succeeded: { label: 'Succeeded', tone: 'emerald' },
    failed: { label: 'Failed', tone: 'rose' },
}

// Keys are exactly what the backend writes to audit_log_entries.action
export const AUDIT_ACTION = {
    incident_created: { label: 'Incident created', tone: 'slate' },
    decision_proposed: { label: 'Decision proposed', tone: 'slate' },
    policy_approved: { label: 'Policy passed', tone: 'emerald' },
    policy_denied: { label: 'Policy denied', tone: 'rose' },
    approval_requested: { label: 'Approval requested', tone: 'indigo' },
    slack_notified: { label: 'Slack notified', tone: 'slate' },
    approval_approved: { label: 'Approved', tone: 'emerald' },
    approval_rejected: { label: 'Rejected', tone: 'rose' },
    action_in_progress: { label: 'Action running', tone: 'amber' },
    action_succeeded: { label: 'Action succeeded', tone: 'emerald' },
    action_failed: { label: 'Action failed', tone: 'rose' },
}

const fallback = (value) => ({ label: value ?? 'Unknown', tone: 'slate' })
export const getIncidentStatus = (s) => INCIDENT_STATUS[s] ?? fallback(s)
export const getActionStatus = (s) => ACTION_STATUS[s] ?? fallback(s)
export const getAuditAction = (a) => AUDIT_ACTION[a] ?? fallback(a)