import Sidebar from './components/Sidebar'
import Header from './components/Header'
import StatCard from './components/StatCard'
import SentinelScoreCard from './components/SentinelScoreCard'
import RemediationActionsList from './components/RemediationActionsList'
import LiveIncidentFeed from './components/LiveIncidentFeed'

const remediationActions = [
  { id: 1, title: "Scaled checkout-api 3 → 6 replicas", subtitle: "High latency detected · policy-approved", status: "Resolved", time: "2m ago" },
  { id: 2, title: "Restarted pod payments-worker-7f9d", subtitle: "CrashLoopBackOff · idempotent restart", status: "Resolved", time: "14m ago" },
  { id: 3, title: "Rolled back inventory-svc to rev. 12", subtitle: "Error rate spike after deploy", status: "In progress", time: "21m ago" },
]

const liveIncidents = [
  { id: 1, title: "auth-service — OOMKilled / restart loop", subtitle: "namespace: production-auth · awaiting approval", status: "Awaiting Approval", time: "just now" },
  { id: 2, title: "inventory-svc — elevated 5xx rate", subtitle: "namespace: prod · rollback in progress", status: "Remediating", time: "21m ago" },
]

function App() {
  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <div className="bg-[#05060a] min-h-screen" style={{ flex: 1 }}>
        <Header />
        <div className="flex items-start gap-4 p-6">
          <SentinelScoreCard score={86} maxScore={100} nodesLabel="Nodes 5/5" podsLabel="Pods 42/45" />
          <StatCard value="2" label="Active incidents" subtext="+1 vs yesterday" accentColor="red" />
          <StatCard value="11" label="Auto-resolved today" subtext="92% success rate" accentColor="green" />
          <StatCard value="1m 48s" label="Avg. time to remediate" subtext="steady" accentColor="white" />
          <StatCard value="17" label="Actions taken (24h)" subtext="4 rollbacks" accentColor="white" />
        </div>
        <div className="px-6 flex flex-col gap-4">
          <RemediationActionsList actions={remediationActions} />
          <LiveIncidentFeed incidents={liveIncidents} />
        </div>
      </div>
    </div>
  )
}

export default App