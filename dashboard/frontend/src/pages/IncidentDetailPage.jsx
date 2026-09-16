import { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import IncidentStatusBadge from '../components/incidents/IncidentStatusBadge';
import IncidentMetadataCard from '../components/incidents/IncidentMetadataCard';
import IncidentRecentLogsCard from '../components/incidents/IncidentRecentLogsCard';
import IncidentWorkflowSteps from '../components/incidents/IncidentWorkflowSteps';

const IncidentDetailPage = () => {
  const { id } = useParams();
  const [incidentStatus, setIncidentStatus] = useState('Awaiting Approval');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const incidentData = {
    id: id || 'WRD-2299',
    service: 'auth-service',
    title: 'OOMKilled / restart loop',
    namespace: 'production-auth',
    cluster: 'us-east-1-main',
    image: 'auth-srv:v2.4.1-rc3',
    duration: '4m 12s',
    assignee: 'Autonomous',
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div>
        {/* Back Link */}
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
              {incidentData.service}
              <span className="font-normal text-slate-400"> — </span>
              {incidentData.title}
            </h1>
            <p className="mt-1 font-mono text-xs sm:text-sm text-slate-400">
              {incidentData.namespace}
              <span className="mx-2 text-slate-600">·</span>
              <span>incident {incidentData.id.startsWith('WRD') ? incidentData.id : `WRD-2299`}</span>
            </p>
          </div>

          <div className="flex items-center gap-3 sm:self-start">
            <IncidentStatusBadge status={incidentStatus} />
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
            namespace={incidentData.namespace}
            cluster={incidentData.cluster}
            image={incidentData.image}
            duration={incidentData.duration}
            assignee={incidentData.assignee}
          />
          <IncidentRecentLogsCard />
        </div>

        {/* Right Column */}
        <div className="lg:col-span-8 xl:col-span-8">
          <IncidentWorkflowSteps onApprovalChange={setIncidentStatus} />
        </div>
      </div>
    </div>
  );
};

export default IncidentDetailPage;
