import IncidentStatusBadge from './IncidentStatusBadge';

const borderColorMap = {
  'Awaiting Approval': 'border-l-amber-500',
  Remediating: 'border-l-yellow-400',
  Resolved: 'border-l-emerald-500',
  Warning: 'border-l-orange-500',
};

const IncidentCard = ({ incident }) => {
  const borderColor = borderColorMap[incident.status] || 'border-l-slate-500';

  return (
    <div
      className={`group flex items-center justify-between rounded-lg border-l-[3px] bg-slate-800/40 px-5 py-4 transition-all duration-200 hover:bg-slate-800/70 ${borderColor}`}
    >
      {/* Left: incident info */}
      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold text-white truncate">
          {incident.service}
          <span className="text-slate-400 font-normal"> — </span>
          {incident.title}
        </p>
        <p className="mt-1 text-xs text-slate-500 truncate">
          {incident.namespace}
          {incident.detail && (
            <>
              <span className="mx-1.5 text-slate-600">·</span>
              {incident.detail}
            </>
          )}
        </p>
      </div>

      {/* Right: badge + time */}
      <div className="ml-4 flex flex-col items-end gap-1.5 flex-shrink-0">
        <IncidentStatusBadge status={incident.status} />
        <span className="text-[11px] text-slate-500">{incident.time}</span>
      </div>
    </div>
  );
};

export default IncidentCard;
