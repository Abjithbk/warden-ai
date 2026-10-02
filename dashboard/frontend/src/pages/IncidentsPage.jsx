import { useState, useMemo } from 'react';
import PageHeader from '../components/common/PageHeader';
import FilterTabs from '../components/common/FilterTabs';
import IncidentCard from '../components/incidents/IncidentCard';

// Mock data matching the design 
const mockIncidents = [
  {
    id: 'inc-001',
    service: 'auth-service',
    title: 'OOMKilled / restart loop',
    namespace: 'production-auth / auth-service',
    detail: 'memory.usage > 95% limit',
    status: 'Awaiting Approval',
    time: 'just now',
    category: 'awaiting',
  },
  {
    id: 'inc-002',
    service: 'inventory-svc',
    title: 'elevated 5xx rate',
    namespace: 'prod / inventory-svc',
    detail: 'error_rate > 8%',
    status: 'Remediating',
    time: '21m ago',
    category: 'warning',
  },
  {
    id: 'inc-003',
    service: 'payments-worker',
    title: 'CrashLoopBackOff',
    namespace: 'prod / payments-worker-7f9d',
    detail: 'pod restart count > 3',
    status: 'Resolved',
    time: '14m ago',
    category: 'resolved',
  },
  {
    id: 'inc-004',
    service: 'checkout-api',
    title: 'memory pressure',
    namespace: 'prod / checkout-api',
    detail: 'node OOM risk detected',
    status: 'Resolved',
    time: '2h ago',
    category: 'resolved',
  },
  {
    id: 'inc-005',
    service: 'recommendation-svc',
    title: 'feature flag rollback',
    namespace: 'prod / recommendation-svc',
    detail: 'anomalous error signature',
    status: 'Resolved',
    time: '1d ago',
    category: 'resolved',
  },
  {
    id: 'inc-006',
    service: 'auth-service',
    title: 'pod restart loop',
    namespace: 'prod / auth-service',
    detail: 'liveness probe failing',
    status: 'Resolved',
    time: '6h ago',
    category: 'resolved',
  },
];

const IncidentsPage = () => {
  const [activeTab, setActiveTab] = useState('all');

  // Compute tab counts from data
  const counts = useMemo(() => {
    const c = { all: 0, awaiting: 0, warning: 0, resolved: 0 };
    mockIncidents.forEach((inc) => {
      c.all++;
      if (c[inc.category] != null) c[inc.category]++;
    });
    return c;
  }, []);

  const tabs = [
    { key: 'all', label: 'All', count: counts.all },
    { key: 'awaiting', label: 'Awaiting Approval', count: counts.awaiting },
    { key: 'warning', label: 'Warning', count: counts.warning },
    { key: 'resolved', label: 'Resolved', count: counts.resolved },
  ];

  // Filter incidents based on active tab
  const filteredIncidents = useMemo(() => {
    if (activeTab === 'all') return mockIncidents;
    return mockIncidents.filter((inc) => inc.category === activeTab);
  }, [activeTab]);

  return (
    <div>
      <PageHeader
        title="Incidents"
        subtitle="Detected anomalies across the cluster"
      />
      <FilterTabs tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

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
    </div>
  );
};

export default IncidentsPage;
