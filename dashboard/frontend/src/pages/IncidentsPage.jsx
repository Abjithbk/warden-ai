import { useState, useEffect, useMemo } from 'react';
import PageHeader from '../components/common/PageHeader';
import FilterTabs from '../components/common/FilterTabs';
import IncidentCard from '../components/incidents/IncidentCard';
import { getIncidents } from '../api/client';
const formatTimeAgo = (dateString) => {
  if (!dateString) return 'recently';
  const seconds = Math.floor((new Date() - new Date(dateString)) / 1000);
  if (seconds < 60) return 'just now';
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function mapStatusToCategory(status) {
  if (status === 'awaiting_approval') return 'awaiting';
  if (status === 'active' || status === 'remediating') return 'warning';
  if (status === 'resolved') return 'resolved';
  return 'all';
}
function mapStatusToDisplay(status) {
  if (status === 'awaiting_approval') return 'Awaiting Approval';
  if (status === 'remediating') return 'Remediating';
  if (status === 'active') return 'Active';
  if (status === 'resolved') return 'Resolved';
  if (status === 'rejected') return 'Rejected';
  return status;
}
const IncidentsPage = () => {
  const [incidents, setIncidents] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  useEffect(() => {
    async function fetchIncidentsData() {
      try {
        setLoading(true);
        setError(null);
        const data = await getIncidents({ limit: 50 });

        const mapped = (data.items || []).map((inc) => ({
          id: `inc-${String(inc.id).padStart(3, '0')}`,
          rawId: inc.id,
          service: inc.service,
          title: inc.title,
          namespace: `${inc.namespace || 'default'} / ${inc.service}`,
          detail: `Severity: ${inc.severity}`,
          status: mapStatusToDisplay(inc.status),
          time: formatTimeAgo(inc.created_at),
          category: mapStatusToCategory(inc.status),
        }));
        setIncidents(mapped);
      } catch (err) {
        console.error('Failed to load incidents:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchIncidentsData();
  }, []);
  // Compute tab counts dynamically from live database data
  const counts = useMemo(() => {
    const c = { all: incidents.length, awaiting: 0, warning: 0, resolved: 0 };
    incidents.forEach((inc) => {
      if (c[inc.category] != null) c[inc.category]++;
    });
    return c;
  }, [incidents]);
  const tabs = [
    { key: 'all', label: 'All', count: counts.all },
    { key: 'awaiting', label: 'Awaiting Approval', count: counts.awaiting },
    { key: 'warning', label: 'Warning', count: counts.warning },
    { key: 'resolved', label: 'Resolved', count: counts.resolved },
  ];
  // Filter incidents based on active tab
  const filteredIncidents = useMemo(() => {
    if (activeTab === 'all') return incidents;
    return incidents.filter((inc) => inc.category === activeTab);
  }, [activeTab, incidents]);

  return (
    <div>
      <PageHeader
        title="Incidents"
        subtitle="Detected anomalies across the cluster"
      />
      <FilterTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {
        error && (
          <div className="mb-4 rounded-lg border border-red-800 bg-red-950/60 p-3 text-sm text-red-200">
            Failed to load incidents: {error}
          </div>
        )
      }

      {loading ? (
        <div className="flex items-center justify-center py-16 text-sm text-slate-400">
          Loading incidents from Supabase...
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {filteredIncidents.map((incident) => (
            <IncidentCard key={incident.id} incident={incident} />
          ))}

          {filteredIncidents.length === 0 && (
            <div className="flex items-center justify-center rounded-lg border border-dashed border-slate-700 py-16 text-sm text-slate-500">
              No incidents in this category
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default IncidentsPage;
