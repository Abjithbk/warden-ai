import { useEffect, useState } from 'react'
import Header from '../components/Header'
import StatCard from '../components/StatCard'
import SentinelScoreCard from '../components/SentinelScoreCard'
import RemediationActionsList from '../components/RemediationActionsList'
import LiveIncidentFeed from '../components/LiveIncidentFeed'
import { getOverviewStats, getRecentActions, getIncidents } from '../api/client'

// Helper to format ISO timestamps into relative "time ago"
function formatTimeAgo(dateString) {
  if (!dateString) return 'recently'
  const seconds = Math.floor((new Date() - new Date(dateString)) / 1000)
  if (seconds < 60) return 'just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

// Helper to format average remediation seconds into "Xm Ys"
function formatDuration(seconds) {
  if (seconds == null || isNaN(seconds)) return '0s'
  const s = Math.round(seconds)
  if (s < 60) return `${s}s`
  const m = Math.floor(s / 60)
  const rem = s % 60
  return rem > 0 ? `${m}m ${rem}s` : `${m}m`
}

function mapActionStatus(status) {
  if (status === 'completed' || status === 'Resolved') return 'Resolved'
  if (status === 'in_progress' || status === 'In progress') return 'In progress'
  if (status === 'failed' || status === 'Failed') return 'Failed'
  return status || 'Pending'
}

function mapIncidentStatus(status) {
  if (status === 'awaiting_approval') return 'Awaiting Approval'
  if (status === 'remediating') return 'Remediating'
  if (status === 'active') return 'Active'
  if (status === 'resolved') return 'Resolved'
  return status || 'Active'
}

function Dashboard() {
  const [stats, setStats] = useState({
    sentinel_score: 95,
    active_incidents: 0,
    auto_resolved_today: 0,
    avg_remediation_seconds: null,
    actions_last_24h: 0,
  })
  const [remediationActions, setRemediationActions] = useState([])
  const [liveIncidents, setLiveIncidents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadDashboardData() {
      try {
        setLoading(true)
        setError(null)

        // Parallel requests using the centralized Axios client
        const [statsData, actionsData, incidentsData] = await Promise.all([
          getOverviewStats(),
          getRecentActions(5),
          getIncidents({ limit: 5 }),
        ])

        setStats(statsData)

        // Transform recent actions for RemediationActionsList component
        setRemediationActions(
          (actionsData || []).map((act) => ({
            id: act.id,
            title: `${act.action_type?.replace('_', ' ') || 'Action'} on ${act.service || act.target}`,
            subtitle: act.incident_title || `Target: ${act.target}`,
            status: mapActionStatus(act.status),
            time: formatTimeAgo(act.completed_at || act.started_at),
          }))
        )

        // Transform incidents for LiveIncidentFeed component
        setLiveIncidents(
          (incidentsData.items || []).map((inc) => ({
            id: inc.id,
            title: `${inc.service} — ${inc.title}`,
            subtitle: `namespace: ${inc.namespace || 'default'} · severity: ${inc.severity}`,
            status: mapIncidentStatus(inc.status),
            time: formatTimeAgo(inc.created_at),
          }))
        )
      } catch (err) {
        console.error('Error fetching dashboard data:', err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  return (
    <div className="bg-slate-950 min-h-screen text-slate-100">
      <Header />

      {error && (
        <div className="mx-4 mt-3 rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200 flex items-center justify-between">
          <span>Failed to connect to backend: {error}</span>
          <button
            onClick={() => window.location.reload()}
            className="rounded bg-red-800/80 px-2 py-1 text-xs hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      )}

      <div className="flex flex-col items-stretch gap-3 p-4 lg:flex-row">
        {/* Sentinel Score */}
        <SentinelScoreCard
          score={stats.sentinel_score}
          maxScore={100}
          nodesLabel="Nodes 5/5"
          podsLabel="Pods 42/45"
        />

        {/* 4 Stat Cards */}
        <div className="flex min-w-0 flex-1 flex-col gap-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              value={loading ? '...' : String(stats.active_incidents)}
              label="Active incidents"
              subtext={stats.active_incidents > 0 ? 'Requires attention' : 'All clear'}
              accentColor={stats.active_incidents > 0 ? 'red' : 'green'}
              subtextColor={stats.active_incidents > 0 ? 'red' : 'green'}
            />
            <StatCard
              value={loading ? '...' : String(stats.auto_resolved_today)}
              label="Auto-resolved today"
              subtext="Handled by Warden"
              accentColor="green"
              subtextColor="green"
            />
            <StatCard
              value={loading ? '...' : formatDuration(stats.avg_remediation_seconds)}
              label="Avg. time to remediate"
              subtext="Automated actions"
              accentColor="white"
            />
            <StatCard
              value={loading ? '...' : String(stats.actions_last_24h)}
              label="Actions taken (24h)"
              subtext="Remediation log"
              accentColor="white"
              subtextColor="green"
            />
          </div>

          {/* Remediation Actions List */}
          <RemediationActionsList actions={remediationActions} />
        </div>
      </div>

      {/* Live Incident Feed */}
      <div className="px-4 pb-4">
        <LiveIncidentFeed incidents={liveIncidents} />
      </div>
    </div>
  )
}

export default Dashboard
