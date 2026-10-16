import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import IncidentStatusBadge from '../components/incidents/IncidentStatusBadge';
import IncidentMetadataCard from '../components/incidents/IncidentMetadataCard';
import IncidentRecentLogsCard from '../components/incidents/IncidentRecentLogsCard';
import IncidentWorkflowSteps from '../components/incidents/IncidentWorkflowSteps';
import { getIncidentById, approveIncident, rejectIncident } from '../api/client';

function calculateDuration(startStr, endStr) {
  if (!startStr) return '0m 00s';
  const start = new Date(startStr);
  const end = endStr ? new Date(endStr) : new Date();
  const diffSec = Math.max(0, Math.floor((end - start) / 1000));
  const m = Math.floor(diffSec / 60);
  const s = diffSec % 60;
  return `${m}m ${s < 10 ? '0' : ''}${s}s`;
}

function mapStatusToBadge(status) {
  if (status === 'awaiting_approval') return 'Awaiting Approval';
  if (status === 'remediating') return 'Remediating';
  if (status === 'resolved') return 'Resolved';
  if (status === 'rejected') return 'Rejected';
  return 'Active';
}

const IncidentDetailPage = () => {
  const { id } = useParams();
  const [incident, setIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Normalize id: handles both 'inc-097' and '97'
  const numericId = id ? id.replace(/^inc-/, '') : null;

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const fetchIncident = async () => {
    if (!numericId) return;
    try {
      setLoading(true);
      setError(null);
      const data = await getIncidentById(numericId);
      setIncident(data);
    } catch (err) {
      console.error('Failed to load incident detail:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIncident();
  }, [numericId]);

  const handleApprove = async () => {
    if (!numericId || actionLoading) return;
    try {
      setActionLoading(true);
      await approveIncident(numericId, { actioned_by: 'dashboard:operator' });
      // Refresh detail data after approval
      await fetchIncident();
    } catch (err) {
      alert(`Approval failed: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!numericId || actionLoading) return;
    const reason = prompt('Please enter the reason for rejection:', 'Operator rejected action');
    if (!reason) return;

    try {
      setActionLoading(true);
      await rejectIncident(numericId, {
        actioned_by: 'dashboard:operator',
        reason: reason,
      });
      // Refresh detail data after rejection
      await fetchIncident();
    } catch (err) {
      alert(`Rejection failed: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center text-sm text-slate-400">
        Loading incident trace #{id}...
      </div>
    );
  }

  if (error || !incident) {
    return (
      <div className="space-y-4">
        <Link to="/incidents" className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white">
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Back to incidents</span>
        </Link>
        <div className="rounded-lg border border-red-800 bg-red-950/60 p-4 text-sm text-red-200">
          Failed to load incident: {error || 'Incident not found'}
        </div>
      </div>
    );
  }

  const duration = calculateDuration(incident.created_at, incident.resolved_at);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        <Link
          to="/incidents"
          className="group inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 hover:text-white transition-colors mb-2"
        >
          <ArrowLeft className="h-3.5 w-3.5 transition-transform group-hover:-translate-x-0.5" />
          <span>Back to incidents</span>
        </Link>

        {/* Title + Status Row */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">
              {incident.service}
              <span className="font-normal text-slate-400"> — </span>
              {incident.title}
            </h1>
            <p className="mt-1 font-mono text-xs sm:text-sm text-slate-400">
              {incident.namespace}
              <span className="mx-2 text-slate-600">·</span>
              <span>incident #{incident.id}</span>
              <span className="mx-2 text-slate-600">·</span>
              <span className="uppercase text-amber-400 font-semibold">{incident.severity}</span>
            </p>
          </div>

          <div className="flex items-center gap-3 sm:self-start">
            <IncidentStatusBadge status={mapStatusToBadge(incident.status)} />
            <span className="font-mono text-sm tabular-nums text-slate-500">
              {currentTime.toLocaleTimeString('en-GB')}
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Column (Metadata + Logs) & Right Column (Workflow Steps) */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
        {/* Left Column */}
        <div className="space-y-4 lg:col-span-4 xl:col-span-4">
          <IncidentMetadataCard
            namespace={incident.namespace || 'default'}
            cluster="production-cluster"
            image={`${incident.service}:v1.0.0`}
            duration={duration}
            assignee="Autonomous (Warden)"
          />
          <IncidentRecentLogsCard />
        </div>

        {/* Right Column */}
        <div className="lg:col-span-8 xl:col-span-8">
          <IncidentWorkflowSteps
            incident={incident}
            onApprove={handleApprove}
            onReject={handleReject}
            actionLoading={actionLoading}
          />
        </div>
      </div>
    </div>
  );
};

export default IncidentDetailPage;
