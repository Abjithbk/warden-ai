import PageHeader from '../components/common/PageHeader'
import StatCard from '../components/StatCard'
import SentinelScoreCard from '../components/SentinelScoreCard'
import RemediationActionsList from '../components/RemediationActionsList'
import LiveIncidentFeed from '../components/LiveIncidentFeed'
import { useIncidents, useOverviewStats, useRecentActions } from '../api/queries'
import { formatDuration } from '../utils/format'

const OPEN_STATUSES = ['active', 'awaiting_approval', 'remediating']

function Dashboard() {
  const stats = useOverviewStats()
  const actions = useRecentActions(5)
  const feed = useIncidents({ limit: 20 })

  const s = stats.data
  const loading = stats.isPending
  const error = stats.error || actions.error || feed.error
  const show = (value) => (loading ? '...' : String(value ?? '—'))

  // The backend filters by one status at a time, so take the newest 20 and keep the open ones.
  const liveIncidents = (feed.data?.items ?? [])
    .filter((incident) => OPEN_STATUSES.includes(incident.status))
    .slice(0, 5)

  const hasOpen = (s?.active_incidents ?? 0) > 0

  return (
    <div>
      <PageHeader title="Overview" subtitle="Live cluster status">
        {s && (
          <span
            className={`flex items-center gap-2 rounded-full border px-3 py-1 text-sm ${hasOpen
                ? 'border-amber-800 bg-amber-950 text-amber-400'
                : 'border-emerald-800 bg-emerald-950 text-emerald-400'
              }`}
          >
            <span className={`h-2 w-2 rounded-full ${hasOpen ? 'bg-amber-400' : 'bg-emerald-400'}`} />
            {hasOpen ? `${s.active_incidents} active` : 'All clear'}
          </span>
        )}
      </PageHeader>

      {error && (
        <div className="mb-4 flex items-center justify-between rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
          <span>Failed to load dashboard data: {error.message}</span>
          <button
            onClick={() => {
              stats.refetch()
              actions.refetch()
              feed.refetch()
            }}
            className="rounded bg-red-800/80 px-2 py-1 text-xs transition hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      )}

      <div className="flex flex-col items-start gap-3 lg:flex-row">
        <SentinelScoreCard score={s?.sentinel_score} loading={loading} />

        <div className="flex min-w-0 flex-1 flex-col gap-3">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              value={show(s?.active_incidents)}
              label="Active incidents"
              subtext={hasOpen ? 'Requires attention' : 'All clear'}
              accentColor={hasOpen ? 'red' : 'green'}
              subtextColor={hasOpen ? 'red' : 'green'}
            />
            <StatCard
              value={show(s?.auto_resolved_today)}
              label="Resolved today"
              subtext="Auto and approved"
              accentColor="green"
              subtextColor="green"
            />
            <StatCard
              value={loading ? '...' : formatDuration(s?.avg_remediation_seconds)}
              label="Avg. time to resolve"
              subtext="Detection to resolved"
              accentColor="white"
            />
            <StatCard
              value={show(s?.actions_last_24h)}
              label="Actions taken (24h)"
              subtext="Remediation log"
              accentColor="white"
              subtextColor="green"
            />
          </div>

          <RemediationActionsList actions={actions.data ?? []} />
        </div>
      </div>

      <div className="mt-3">
        <LiveIncidentFeed incidents={liveIncidents} />
      </div>
    </div>
  )
}

export default Dashboard