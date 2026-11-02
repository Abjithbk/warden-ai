import PageHeader from '../components/common/PageHeader'
import PolicyCard from '../components/PolicyCard'

// Static for now. These guardrails are the design targets for M5 (OPA/Rego);
// nothing enforces them yet. Replace with data from the policy engine later.
const POLICIES = [
  {
    icon: 'RotateCcw',
    title: 'Pod Restart',
    description: 'Deletes a crash-looping or unresponsive pod so the Deployment controller recreates it fresh.',
    guardrails: ['Max 3 restarts per pod per hour', 'Pre-action state check for idempotency'],
    enabled: true,
  },
  {
    icon: 'Monitor',
    title: 'Scale Deployment',
    description: 'Patches replica count in response to latency or load-driven anomalies.',
    guardrails: ['Hard ceiling of 10 replicas per service', '5-minute cooldown between scale actions'],
    enabled: true,
  },
  {
    icon: 'RotateCcw',
    title: 'Rollback Deployment',
    description: 'Reverts to a previous Deployment revision when a recent release correlates with the incident.',
    guardrails: ['Only within the last 5 revisions', 'Requires a deploy event within 15 min prior'],
    enabled: false,
  },
  {
    icon: 'Flag',
    title: 'Toggle Feature Flag',
    description: 'Switches a feature flag off or on when a flagged feature correlates with the incident.',
    guardrails: ['Guardrails to be defined in the M5 policy rules'],
    enabled: false,
  },
]

function ActionPolicyPage() {
  return (
    <div>
      <PageHeader
        title="Action Policy"
        subtitle="The complete whitelist of remediation actions Warden may take"
      />
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        {POLICIES.map((policy) => (
          <PolicyCard key={policy.title} {...policy} />
        ))}
      </div>
    </div>
  )
}

export default ActionPolicyPage