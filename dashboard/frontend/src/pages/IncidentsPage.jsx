import { useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import FilterTabs from '../components/common/FilterTabs'
import Pagination from '../components/common/Pagination'
import IncidentCard from '../components/incidents/IncidentCard'
import { useIncidents } from '../api/queries'

const PAGE_SIZE = 20
const TABS = [
  { key: 'all', label: 'All' },
  { key: 'awaiting_approval', label: 'Awaiting Approval' },
  { key: 'active', label: 'Active' },
  { key: 'remediating', label: 'Remediating' },
  { key: 'resolved', label: 'Resolved' },
  { key: 'rejected', label: 'Rejected' },
]

const IncidentsPage = () => {
  const [tab, setTab] = useState('all')
  const [page, setPage] = useState(0)

  const params = {
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
    ...(tab !== 'all' && { status: tab }),
  }
  const { data, error, isPending } = useIncidents(params)
  const items = data?.items ?? []
  const total = data?.total ?? 0

  const changeTab = (key) => {
    setTab(key)
    setPage(0)
  }

  return (
    <div>
      <PageHeader title="Incidents" subtitle="Detected anomalies across the cluster" />
      <FilterTabs tabs={TABS} activeTab={tab} onTabChange={changeTab} />

      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
          Failed to load incidents: {error.message}
        </div>
      )}

      {isPending ? (
        <div className="py-16 text-center text-sm text-slate-400">Loading incidents...</div>
      ) : items.length === 0 ? (
        <div className="rounded-lg border border-dashed border-slate-700 py-16 text-center text-sm text-slate-500">
          No incidents in this category
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {items.map((incident) => (
            <IncidentCard key={incident.id} incident={incident} />
          ))}
        </div>
      )}

      <Pagination page={page} pageSize={PAGE_SIZE} total={total} onChange={setPage} />
    </div>
  )
}

export default IncidentsPage