import { useState, useEffect } from 'react';
import PolicyCard from '../components/PolicyCard';

const policies = [
  {
    icon: 'RotateCcw',
    title: 'Pod Restart',
    description: 'Deletes a crash-looping or unresponsive pod so the Deployment controller recreates it fresh.',
    guardrails: [
      'Max 3 restarts per pod per hour',
      'Pre-action state check for idempotency',
    ],
    enabled: true,
  },
  {
    icon: 'Monitor',
    title: 'Scale Deployment',
    description: 'Patches replica count in response to latency or load-driven anomalies.',
    guardrails: [
      'Hard ceiling of 10 replicas per service',
      '5-minute cooldown between scale actions',
    ],
    enabled: true,
  },
  {
    icon: 'RotateCcw',
    title: 'Rollback Deployment',
    description: 'Reverts to a previous Deployment revision when a recent release correlates with the incident.',
    guardrails: [
      'Only within the last 5 revisions',
      'Requires a deploy event within 15 min prior',
    ],
    enabled: false,
  },
  {
    icon: 'Flag',
    title: 'Feature Flag Toggle',
    description: 'Disables a LaunchDarkly flag tied to a recently-shipped code path implicated in the anomaly.',
    guardrails: [
      'Only pre-registered flags are toggleable',
      'Auto re-enable review after 24h',
    ],
    enabled: true,
  },
];

function ActionPolicyPage() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="px-8 py-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Action Policy</h1>
          <p className="mt-1 text-sm text-slate-400">
            The complete whitelist of remediation actions Warden may take
          </p>
        </div>
        <div className="font-mono text-sm text-slate-500">
          {currentTime.toLocaleTimeString('en-GB')}
        </div>
      </div>

      <div className="mt-6">
        <PolicyCard
          icon="RotateCcw"
          title="Pod Restart"
          description="Deletes a crash-looping or unresponsive pod so the Deployment controller recreates it fresh."
          guardrails={['Max 3 restarts per pod per hour', 'Pre-action state check for idempotency']}
          enabled={true}
        />
      </div>
    </div>
  );
}

export default ActionPolicyPage;