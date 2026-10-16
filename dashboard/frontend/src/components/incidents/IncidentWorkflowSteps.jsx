import {
  CircleDot,
  CheckCircle2,
  Shield,
  Check,
  X,
  Play,
  Activity,
  Terminal,
  Send,
  Loader2,
} from 'lucide-react';

const card =
  'rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm';
const pending =
  'rounded border border-slate-700/50 bg-slate-800/80 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-slate-500';

const formatTime = (iso) => (iso ? `${new Date(iso).toISOString().slice(11, 19)} UTC` : null);
const humanize = (value) => (value || '').replace(/_/g, ' ');

// "slack:amaya" -> { via: 'Slack', name: 'amaya' }
function parseActor(actor) {
  if (!actor) return { via: null, name: 'unknown' };
  const [source, ...rest] = actor.split(':');
  if (!rest.length) return { via: null, name: actor };
  return { via: source === 'slack' ? 'Slack' : 'Dashboard', name: rest.join(':') };
}

function traceLine(item) {
  const label = item.step ?? item.name ?? 'step';
  const out = item.output ?? item.result ?? item;
  return `${label}: ${typeof out === 'string' ? out : JSON.stringify(out)}`;
}

const TimeOrPending = ({ iso }) =>
  iso ? (
    <span className="font-mono text-xs text-slate-500">{formatTime(iso)}</span>
  ) : (
    <span className={pending}>PENDING</span>
  );

const IncidentWorkflowSteps = ({
  incident,
  onApprove,
  onReject,
  onNotifySlack,
  actionLoading = false,
  notifyLoading = false,
}) => {
  // Backend returns every list oldest -> newest, so the last item is current.
  const detection = incident.detections?.at(-1);
  const decision = incident.agent_decisions?.at(-1);
  const policy = incident.policy_checks?.at(-1);
  const approval = incident.approval_requests?.at(-1);
  const action = incident.remediation_actions?.at(-1);

  const approvalState = !approval
    ? 'none'
    : approval.status === 'pending'
      ? actionLoading
        ? 'approving'
        : 'awaiting'
      : approval.status === 'approved'
        ? 'approved'
        : 'denied';

  const actor = parseActor(approval?.actioned_by);
  const sentToSlack = Boolean(approval?.slack_message_ts);
  const policyDenied = policy?.verdict === 'denied';
  const executed = action?.status === 'succeeded';

  return (
    <div className="space-y-3.5">
      {/* STEP 1: DIAGNOSE */}
      <div className={card}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <CircleDot className="h-4 w-4 text-slate-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              STEP 1: DIAGNOSE
            </h4>
          </div>
          <TimeOrPending iso={decision?.created_at || detection?.created_at} />
        </div>

        {!decision ? (
          <p className="mt-3 text-sm text-slate-400">Waiting for the agent to diagnose...</p>
        ) : (
          <div className="mt-3.5 rounded-lg border border-slate-800/90 bg-[#070d19] p-3.5 font-mono text-xs leading-relaxed text-slate-300 shadow-inner">
            <div className="mb-2 font-semibold text-slate-400">Analysis:</div>
            <div className="space-y-1.5 pl-1">
              <div>
                <span className="text-slate-500">· </span>
                <span className="text-amber-400">Target:</span>{' '}
                <span className="text-slate-200">{decision.target}</span>
              </div>
              {detection && (
                <div>
                  <span className="text-slate-500">· </span>
                  <span className="text-amber-400">Signal:</span>{' '}
                  <span className="text-slate-200">
                    {detection.signal} ({detection.source})
                  </span>
                </div>
              )}
              <div>
                <span className="text-slate-500">· </span>
                <span className="text-amber-400">Confidence:</span>{' '}
                <span className="text-slate-200">{Math.round(decision.confidence * 100)}%</span>
              </div>
              {decision.reasoning_trace?.map((item, idx) => (
                <div key={idx}>
                  <span className="text-slate-500">· </span>
                  <span className="text-slate-200">{traceLine(item)}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* STEP 2: DECIDE */}
      <div className={card}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="relative flex h-4 w-4 items-center justify-center">
              <span className="absolute h-3 w-3 rounded-full bg-amber-400/20 ring-2 ring-amber-400/50"></span>
              <span className="h-1.5 w-1.5 rounded-full bg-amber-400"></span>
            </div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400">
              STEP 2: DECIDE
            </h4>
          </div>
          <TimeOrPending iso={decision?.created_at} />
        </div>
        <p className="mt-3 text-sm text-slate-300">
          {decision
            ? `Recommended Action: ${humanize(decision.proposed_action)} on ${decision.target}.`
            : 'No action proposed yet.'}
        </p>
      </div>

      {/* STEP 3: POLICY CHECK */}
      <div className={card}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <CheckCircle2
              className={`h-4 w-4 ${policyDenied ? 'text-rose-400' : policy ? 'text-emerald-400' : 'text-slate-500'}`}
            />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              STEP 3: POLICY CHECK
            </h4>
          </div>
          <TimeOrPending iso={policy?.created_at} />
        </div>
        <div className="mt-3 flex items-center gap-2 text-sm text-slate-300">
          {policy ? (
            <>
              {policyDenied ? (
                <X className="h-3.5 w-3.5 text-rose-400" />
              ) : (
                <Check className="h-3.5 w-3.5 text-emerald-400" />
              )}
              <span>
                Status: {policyDenied ? 'Denied' : 'Approved'}. {policy.reason}
                {policy.policy_name && (
                  <span className="text-slate-500"> ({policy.policy_name})</span>
                )}
              </span>
            </>
          ) : (
            <span className="text-slate-400">Waiting for policy check.</span>
          )}
        </div>
      </div>

      {/* STEP 4: HUMAN APPROVAL */}
      <div
        className={`rounded-xl border transition-all duration-300 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm ${approvalState === 'awaiting'
            ? 'border-indigo-500/40 shadow-indigo-950/20'
            : approvalState === 'approving'
              ? 'border-amber-500/40'
              : approvalState === 'approved'
                ? 'border-emerald-500/40'
                : approvalState === 'denied'
                  ? 'border-rose-500/40'
                  : 'border-slate-800/80'
          }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Shield className="h-4 w-4 text-indigo-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
              STEP 4: HUMAN APPROVAL
            </h4>
          </div>
          <TimeOrPending iso={approval?.actioned_at || approval?.created_at} />
        </div>

        <div className="mt-3">
          {approvalState === 'none' && (
            <p className="text-sm text-slate-400">No approval request raised yet.</p>
          )}

          {(approvalState === 'awaiting' || approvalState === 'approving') && (
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <CircleDot className="h-3.5 w-3.5 text-indigo-400" />
                <span>
                  Status: Awaiting Approval
                  <span className="text-slate-500">
                    {sentToSlack
                      ? ' · sent to Slack, can be approved there or here'
                      : ' · not sent to Slack yet'}
                  </span>
                </span>
              </div>

              {approvalState === 'approving' ? (
                <div className="mt-4 flex items-center gap-3 text-sm text-amber-400">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-amber-400 border-t-transparent"></div>
                  <span>Submitting decision...</span>
                </div>
              ) : (
                <div className="mt-4 flex flex-wrap items-center gap-3">
                  <button
                    type="button"
                    onClick={onApprove}
                    className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-md shadow-emerald-500/20 transition-all hover:bg-emerald-400 active:scale-95 cursor-pointer"
                  >
                    <Check className="h-4 w-4 stroke-[2.5]" />
                    <span>Approve Action</span>
                  </button>

                  <button
                    type="button"
                    onClick={onReject}
                    className="flex items-center gap-2 rounded-lg border border-rose-800/60 bg-rose-950/40 px-4 py-2 text-sm font-semibold text-rose-300 transition-all hover:bg-rose-900/50 active:scale-95 cursor-pointer"
                  >
                    <X className="h-4 w-4 stroke-[2.5]" />
                    <span>Deny Action</span>
                  </button>

                  <button
                    type="button"
                    onClick={onNotifySlack}
                    disabled={notifyLoading}
                    className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800/60 px-4 py-2 text-sm font-semibold text-slate-200 transition-all hover:bg-slate-700/60 active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
                  >
                    {notifyLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                    <span>{sentToSlack ? 'Resend to Slack' : 'Send to Slack'}</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {approvalState === 'approved' && (
            <div className="flex items-center gap-2 text-sm text-emerald-400">
              <CheckCircle2 className="h-4 w-4" />
              <span className="font-medium">Status: Action Approved by {actor.name}</span>
              {actor.via && (
                <span className="rounded border border-slate-700/60 bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-300">
                  via {actor.via}
                </span>
              )}
            </div>
          )}

          {approvalState === 'denied' && (
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-sm text-rose-400">
                <X className="h-4 w-4" />
                <span className="font-medium">Status: Action Denied by {actor.name}</span>
                {actor.via && (
                  <span className="rounded border border-slate-700/60 bg-slate-800/80 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-slate-300">
                    via {actor.via}
                  </span>
                )}
              </div>
              {approval.rejection_reason && (
                <p className="text-xs text-slate-400">Reason: {approval.rejection_reason}</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* STEP 5: ACT */}
      <div className={card}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {executed ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            ) : action ? (
              <Play className="h-4 w-4 animate-pulse text-amber-400" />
            ) : (
              <CircleDot className="h-4 w-4 text-slate-500" />
            )}
            <h4
              className={`text-xs font-bold uppercase tracking-wider ${executed ? 'text-slate-200' : 'text-slate-400'}`}
            >
              STEP 5: ACT
            </h4>
          </div>
          <TimeOrPending iso={action?.completed_at || action?.started_at} />
        </div>

        <div className="mt-3 text-sm">
          {action ? (
            <div className="space-y-2">
              <p className={executed ? 'text-slate-300' : 'text-amber-400'}>
                {humanize(action.action_type)} on {action.target}: {humanize(action.status)}
              </p>
              {action.result?.message && (
                <div className="rounded-lg border border-slate-800/90 bg-[#070d19] p-3 font-mono text-xs text-slate-300">
                  <div className="flex items-center gap-2 text-slate-400">
                    <Terminal className="h-3.5 w-3.5 text-sky-400" />
                    <span>{action.result.message}</span>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-slate-400">Waiting for approval to execute the action...</p>
          )}
        </div>
      </div>

      {/* STEP 6: OBSERVE */}
      <div className={card}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {incident.status === 'resolved' ? (
              <Activity className="h-4 w-4 text-emerald-400" />
            ) : (
              <CircleDot className="h-4 w-4 text-slate-500" />
            )}
            <h4
              className={`text-xs font-bold uppercase tracking-wider ${incident.status === 'resolved' ? 'text-slate-200' : 'text-slate-400'}`}
            >
              STEP 6: OBSERVE
            </h4>
          </div>
          <TimeOrPending iso={incident.resolved_at} />
        </div>
        <p className="mt-3 text-sm">
          {incident.status === 'resolved' ? (
            <span className="font-medium text-emerald-400">Incident resolved.</span>
          ) : incident.status === 'rejected' ? (
            <span className="text-slate-400">Action rejected, no remediation was run.</span>
          ) : (
            <span className="text-slate-400">Waiting for remediation to complete.</span>
          )}
        </p>
      </div>
    </div>
  );
};

export default IncidentWorkflowSteps;