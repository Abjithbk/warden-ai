import { useState } from 'react'
import PageHeader from '../components/common/PageHeader'
import SearchBar from '../components/common/SearchBar'
import Pagination from '../components/common/Pagination'
import AuditTable from '../components/audit/AuditTable'
import { useAuditLogs } from '../api/queries'
import { auditExportUrl } from '../api/client'
import { AUDIT_ACTION } from '../constants/status'
import { useDebounce } from '../hooks/useDebounce'

const PAGE_SIZE = 50

// The backend filters are exact-match, so turn the search text into the right one:
//   "12" or "INC-0012" -> incident_id, "approval_approved" -> action, anything else -> actor
function buildFilters(query) {
  const q = query.trim()
  if (!q) return {}
  const idMatch = q.match(/^(?:inc-?)?0*(\d+)$/i)
  if (idMatch) return { incident_id: Number(idMatch[1]) }
  if (q in AUDIT_ACTION) return { action: q }
  return { actor: q }
}

const AuditLog = () => {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(0)
  const debounced = useDebounce(search)

  const filters = buildFilters(debounced)
  const { data, error, isPending } = useAuditLogs({
    ...filters,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  })

  const handleSearch = (value) => {
    setSearch(value)
    setPage(0)
  }

  return (
    <div className="mx-auto max-w-7xl">
      <PageHeader title="Audit Log" subtitle="Every pipeline event, in order">
        <a
          href={auditExportUrl(filters)}
          download
          className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-700 hover:text-white"
        >
          ↓ Export CSV
        </a>
      </PageHeader>

      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
          Failed to load audit log: {error.message}
        </div>
      )}

      <div className="mb-6">
        <SearchBar
          value={search}
          onChange={handleSearch}
          placeholder="Incident ID (e.g. 12), actor (e.g. slack:U123) or event (e.g. policy_denied)"
        />
      </div>

      {isPending ? (
        <div className="py-16 text-center text-sm text-slate-400">Loading audit log...</div>
      ) : (
        <>
          <p className="mb-3 text-xs text-slate-500">{data.total} entries</p>
          <AuditTable entries={data.items} />
          <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onChange={setPage} />
        </>
      )}
    </div>
  )
}

export default AuditLog