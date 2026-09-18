import { useState } from 'react';
import {
  CircleDot,
  CheckCircle2,
  Shield,
  Check,
  X,
  Play,
  Activity,
  RotateCcw,
  Terminal,
} from 'lucide-react';

const IncidentWorkflowSteps = ({ onApprovalChange }) => {
  const [approvalStatus, setApprovalStatus] = useState('awaiting'); // 'awaiting' | 'approving' | 'approved' | 'denied'

  const handleApprove = () => {
    if (approvalStatus !== 'awaiting') return;
    setApprovalStatus('approving');
    if (onApprovalChange) onApprovalChange('Remediating');

    setTimeout(() => {
      setApprovalStatus('approved');
      if (onApprovalChange) onApprovalChange('Resolved');
    }, 1500);
  };

  const handleDeny = () => {
    setApprovalStatus('denied');
    if (onApprovalChange) onApprovalChange('Warning');
  };

  const handleReset = () => {
    setApprovalStatus('awaiting');
    if (onApprovalChange) onApprovalChange('Awaiting Approval');
  };

  return (
    <div className="space-y-3.5">
      {/* STEP 1: DIAGNOSE */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <CircleDot className="h-4 w-4 text-slate-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              STEP 1: DIAGNOSE
            </h4>
          </div>
          <span className="font-mono text-xs text-slate-500">10:42:08 UTC</span>
        </div>

        <p className="mt-3 text-sm text-slate-300">
          LLM detected high memory pressure and pod restart loop.
        </p>

        {/* Analysis subcard */}
        <div className="mt-3.5 rounded-lg border border-slate-800/90 bg-[#070d19] p-3.5 font-mono text-xs leading-relaxed text-slate-300 shadow-inner">
          <div className="mb-2 font-semibold text-slate-400">Analysis:</div>
          <div className="space-y-1.5 pl-1">
            <div>
              <span className="text-slate-500">· </span>
              <span className="text-amber-400">Target:</span>{' '}
              <span className="text-slate-200">pod/auth-service-v2-7f6b9d-xyz</span>
            </div>
            <div>
              <span className="text-slate-500">· </span>
              <span className="text-amber-400">Pattern:</span>{' '}
              <span className="text-slate-200">OOMKilled → CrashLoopBackOff</span>
            </div>
            <div>
              <span className="text-slate-500">· </span>
              <span className="text-amber-400">Metric:</span>{' '}
              <span className="text-slate-200">memory.usage &gt; 95% limit (2Gi)</span>
            </div>
            <div>
              <span className="text-slate-500">· </span>
              <span className="text-amber-400">Root Cause Prob:</span>{' '}
              <span className="text-slate-200">
                Sudden spike in authentication requests causing heap exhaustion.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* STEP 2: DECIDE */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
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
          <span className="font-mono text-xs text-slate-500">10:42:11 UTC</span>
        </div>

        <p className="mt-3 text-sm text-slate-300">
          Recommended Action: Scale horizontal pod autoscaler (HPA) to 10 replicas to distribute memory load.
        </p>
      </div>

      {/* STEP 3: POLICY CHECK */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-200">
              STEP 3: POLICY CHECK
            </h4>
          </div>
          <span className="font-mono text-xs text-slate-500">10:42:12 UTC</span>
        </div>

        <div className="mt-3 flex items-center gap-2 text-sm text-slate-300">
          <Check className="h-3.5 w-3.5 text-emerald-400" />
          <span>Status: Approved. Action matches whitelist (Scale Up).</span>
        </div>
      </div>

      {/* STEP 4: HUMAN APPROVAL */}
      <div
        className={`rounded-xl border transition-all duration-300 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm ${approvalStatus === 'awaiting'
          ? 'border-indigo-500/40 shadow-indigo-950/20'
          : approvalStatus === 'approved'
            ? 'border-emerald-500/40'
            : 'border-rose-500/40'
          }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Shield className="h-4 w-4 text-indigo-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-300">
              STEP 4: HUMAN APPROVAL
            </h4>
          </div>
          <span className="font-mono text-xs text-slate-500">10:42:13 UTC</span>
        </div>

        <div className="mt-3">
          {approvalStatus === 'awaiting' && (
            <div>
              <div className="flex items-center gap-2 text-sm text-slate-300">
                <CircleDot className="h-3.5 w-3.5 text-indigo-400" />
                <span>Status: Awaiting Approval</span>
              </div>

              <div className="mt-4 flex flex-wrap items-center gap-3">
                <button
                  type="button"
                  onClick={handleApprove}
                  className="flex items-center gap-2 rounded-lg bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 shadow-md shadow-emerald-500/20 transition-all hover:bg-emerald-400 active:scale-95 cursor-pointer"
                >
                  <Check className="h-4 w-4 stroke-[2.5]" />
                  <span>Approve Action</span>
                </button>

                <button
                  type="button"
                  onClick={handleDeny}
                  className="flex items-center gap-2 rounded-lg border border-rose-800/60 bg-rose-950/40 px-4 py-2 text-sm font-semibold text-rose-300 transition-all hover:bg-rose-900/50 active:scale-95 cursor-pointer"
                >
                  <X className="h-4 w-4 stroke-[2.5]" />
                  <span>Deny Action</span>
                </button>
              </div>
            </div>
          )}

          {approvalStatus === 'approving' && (
            <div className="flex items-center gap-3 text-sm text-amber-400">
              <div className="h-4 w-4 animate-spin rounded-full border-2 border-amber-400 border-t-transparent"></div>
              <span>Executing approved scale command...</span>
            </div>
          )}

          {approvalStatus === 'approved' && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-emerald-400">
                  <CheckCircle2 className="h-4 w-4" />
                  <span className="font-medium">Status: Action Approved by Operator</span>
                </div>
                <button
                  type="button"
                  onClick={handleReset}
                  className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
                  title="Reset to initial state"
                >
                  <RotateCcw className="h-3.5 w-3.5" />
                  <span>Reset Demo</span>
                </button>
              </div>
            </div>
          )}

          {approvalStatus === 'denied' && (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-rose-400">
                <X className="h-4 w-4" />
                <span>Status: Action Denied by Operator</span>
              </div>
              <button
                type="button"
                onClick={handleReset}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <RotateCcw className="h-3.5 w-3.5" />
                <span>Reset Demo</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* STEP 5: ACT */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {approvalStatus === 'approved' ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            ) : approvalStatus === 'approving' ? (
              <Play className="h-4 w-4 animate-pulse text-amber-400" />
            ) : (
              <CircleDot className="h-4 w-4 text-slate-500" />
            )}
            <h4
              className={`text-xs font-bold uppercase tracking-wider ${approvalStatus === 'approved'
                ? 'text-slate-200'
                : 'text-slate-400'
                }`}
            >
              STEP 5: ACT
            </h4>
          </div>

          {approvalStatus === 'awaiting' || approvalStatus === 'denied' ? (
            <span className="rounded border border-slate-700/50 bg-slate-800/80 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              PENDING
            </span>
          ) : approvalStatus === 'approving' ? (
            <span className="rounded border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-amber-400">
              EXECUTING
            </span>
          ) : (
            <span className="font-mono text-xs text-slate-500">10:42:14 UTC</span>
          )}
        </div>

        <div className="mt-3 text-sm">
          {approvalStatus === 'awaiting' || approvalStatus === 'denied' ? (
            <p className="text-slate-400">Waiting for approval to execute scale command...</p>
          ) : approvalStatus === 'approving' ? (
            <p className="text-amber-400">Executing kubectl scale deployment auth-service --replicas=10...</p>
          ) : (
            <div className="space-y-2">
              <p className="text-slate-300">
                Executed scale command successfully via Kubernetes Cluster API:
              </p>
              <div className="rounded-lg border border-slate-800/90 bg-[#070d19] p-3 font-mono text-xs text-slate-300">
                <div className="flex items-center gap-2 text-slate-400">
                  <Terminal className="h-3.5 w-3.5 text-sky-400" />
                  <span>kubectl scale deployment/auth-service --replicas=10 -n production-auth</span>
                </div>
                <div className="mt-1 text-emerald-400">
                  deployment.apps/auth-service scaled (3 → 10 replicas)
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* STEP 6: OBSERVE */}
      <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            {approvalStatus === 'approved' ? (
              <Activity className="h-4 w-4 text-emerald-400" />
            ) : (
              <CircleDot className="h-4 w-4 text-slate-500" />
            )}
            <h4
              className={`text-xs font-bold uppercase tracking-wider ${approvalStatus === 'approved'
                ? 'text-slate-200'
                : 'text-slate-400'
                }`}
            >
              STEP 6: OBSERVE
            </h4>
          </div>

          {approvalStatus === 'approved' ? (
            <span className="font-mono text-xs text-slate-500">10:42:25 UTC</span>
          ) : (
            <span className="rounded border border-slate-700/50 bg-slate-800/80 px-2 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wider text-slate-500">
              PENDING
            </span>
          )}
        </div>

        <div className="mt-3 text-sm">
          {approvalStatus === 'approved' ? (
            <div className="space-y-1 text-slate-300">
              <p className="text-emerald-400 font-medium">
                Remediation verified: 10/10 pods healthy and running.
              </p>
              <p className="text-slate-400 text-xs">
                Memory utilization normalized to 44% (limit 2Gi). Zero OOMKills detected over the last 10 minutes.
              </p>
            </div>
          ) : (
            <p className="text-slate-400">Waiting for remediation to complete.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default IncidentWorkflowSteps;
