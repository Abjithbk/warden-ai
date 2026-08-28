import React, { useState } from 'react';
import Layout from '../components/layout/Layout';
import SearchBar from '../components/common/SearchBar';
import AuditTable from '../components/audit/AuditTable';

const AuditLog = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const auditData = [
    {
      time: '16:42:13',
      incident: 'WRD-2299',
      service: 'auth-service',
      action: 'scale_deployment',
      result: 'Pending',
      rollback: '-',
    },
    {
      time: '13:41:07',
      incident: 'WRD-2288',
      service: 'inventory-svc',
      action: 'rollback_deployment',
      result: 'In progress',
      rollback: '-',
    },
    {
      time: '13:48:52',
      incident: 'WRD-2286',
      service: 'payments-worker',
      action: 'pod_restart',
      result: 'Success',
      rollback: 'not needed',
    },
    {
      time: '11:59:20',
      incident: 'WRD-2281',
      service: 'checkout-api',
      action: 'scale_deployment',
      result: 'Success',
      rollback: 'not needed',
    },
    {
      time: '09:14:03',
      incident: 'WRD-2277',
      service: 'auth-service',
      action: 'pod_restart',
      result: 'Success',
      rollback: 'not needed',
    },
    {
      time: 'Yesterday',
      incident: 'WRD-2265',
      service: 'recommendation-svc',
      action: 'feature_flag_toggle',
      result: 'Failed',
      rollback: 'rolled back',
    },
  ];

  const filteredData = auditData.filter((row) => {
    const q = searchQuery.toLowerCase();
    return (
      row.service.toLowerCase().includes(q) ||
      row.action.toLowerCase().includes(q) ||
      row.incident.toLowerCase().includes(q)
    );
  });

  const currentTime = new Date().toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  return (
    <Layout>
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-6 flex flex-col gap-4 border-b border-slate-800 pb-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-xl font-semibold text-white sm:text-2xl">
              Audit Log
            </h1>
            <p className="mt-1 text-sm text-slate-400">
              Every remediation action, in order
            </p>
          </div>
          <div className="font-mono text-xs text-slate-500 sm:text-sm">
            {currentTime}
          </div>
        </div>

        {/* Search */}
        <div className="mb-6">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
        </div>

        {/* Table */}
        <AuditTable data={filteredData} />
      </div>
    </Layout>
  );
};

export default AuditLog;