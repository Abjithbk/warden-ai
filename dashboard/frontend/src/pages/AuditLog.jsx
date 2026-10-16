import { useState, useEffect, useMemo } from 'react';
import SearchBar from '../components/common/SearchBar';
import AuditTable from '../components/audit/AuditTable';
import { getAuditLogs } from '../api/client';

// Maps backend action string to a readable result/status
function mapActionToResult(action) {
  if (action === 'action_succeeded') return 'Success';
  if (action === 'action_failed') return 'Failed';
  if (action === 'action_started') return 'In progress';
  if (action === 'approval_approved') return 'Success';
  if (action === 'slack_notified') return 'Success';
  if (action === 'approval_rejected') return 'Failed';
  if (action === 'incident_created') return 'Pending';
  return 'Pending';
}

// Maps backend detail object to a rollback string
function mapDetailToRollback(action, detail) {
  if (action === 'action_succeeded') {
    const type = detail?.action_type || '';
    if (type === 'rollback_deployment') return 'rolled back';
    return 'not needed';
  }
  if (action === 'action_failed') return 'rolled back';
  return '-';
}

// Maps backend actor to a service name from the detail field
function extractService(detail) {
  return detail?.target || detail?.service || detail?.source || '-';
}

// Formats ISO datetime to HH:MM:SS
function formatTime(isoString) {
  if (!isoString) return '-';
  const date = new Date(isoString);
  const now = new Date();
  const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
  if (diffDays >= 1) return `${diffDays}d ago`;
  return date.toLocaleTimeString('en-GB', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });
}

const AuditLog = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [auditData, setAuditData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentTime, setCurrentTime] = useState(() =>
    new Date().toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  );

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(
        new Date().toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
        })
      );
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    async function fetchAuditLogs() {
      try {
        setLoading(true);
        setError(null);

        // Fetch up to 100 entries from Supabase via backend
        const data = await getAuditLogs({ limit: 100 });

        // Transform backend data to match the AuditTable column format
        const mapped = (data.items || []).map((entry) => ({
          id: entry.id,
          time: formatTime(entry.created_at),
          incident: `INC-${String(entry.incident_id).padStart(4, '0')}`,
          incidentRawId: entry.incident_id,
          service: extractService(entry.detail),
          action: entry.action,
          actor: entry.actor,
          result: mapActionToResult(entry.action),
          rollback: mapDetailToRollback(entry.action, entry.detail),
        }));

        setAuditData(mapped);
      } catch (err) {
        console.error('Failed to load audit logs:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchAuditLogs();
  }, []);

  // Filter the fetched data by search query (searches service, action, incident, actor)
  const filteredData = useMemo(() => {
    if (!searchQuery.trim()) return auditData;
    const q = searchQuery.toLowerCase();
    return auditData.filter(
      (row) =>
        row.service.toLowerCase().includes(q) ||
        row.action.toLowerCase().includes(q) ||
        row.incident.toLowerCase().includes(q) ||
        row.actor.toLowerCase().includes(q)
    );
  }, [searchQuery, auditData]);

  return (
    <div className="mx-auto max-w-7xl">
      {/* Header */}
      <div className="mb-6 flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-white sm:text-2xl">Audit Log</h1>
          <p className="mt-1 text-sm text-slate-400">Every remediation action, in order</p>
        </div>
        <div className="flex items-center gap-4">
          {/* CSV Export Button */}
          <a
            href="http://localhost:8000/api/v1/audit/export"
            download
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-700 hover:text-white"
          >
            ↓ Export CSV
          </a>
          <div className="font-mono text-xs text-slate-500 sm:text-sm">{currentTime}</div>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mb-4 rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
          Failed to load audit log: {error}
        </div>
      )}

      {/* Search */}
      <div className="mb-6">
        <SearchBar value={searchQuery} onChange={setSearchQuery} />
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-16 text-sm text-slate-400">
          Loading audit log from Supabase...
        </div>
      ) : (
        <>
          <p className="mb-3 text-xs text-slate-500">
            Showing {filteredData.length} of {auditData.length} entries
          </p>
          <AuditTable data={filteredData} />
        </>
      )}
    </div>
  );
};

export default AuditLog;
