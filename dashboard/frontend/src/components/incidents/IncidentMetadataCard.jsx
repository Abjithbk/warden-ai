const IncidentMetadataCard = ({
  namespace = 'production-auth',
  cluster = 'us-east-1-main',
  image = 'auth-srv:v2.4.1-rc3',
  duration = '4m 12s',
  assignee = 'Autonomous',
}) => {
  const metadataItems = [
    { label: 'Namespace', value: namespace, isMono: true },
    { label: 'Cluster', value: cluster, isMono: true },
    { label: 'Image', value: image, isMono: true },
    { label: 'Duration', value: duration, isMono: true },
    {
      label: 'Assignee',
      customRender: (
        <div className="inline-flex items-center gap-2 rounded-full bg-slate-800/90 border border-slate-700/60 py-0.5 pl-1 pr-3">
          <div className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-600 text-[10px] font-bold text-white shadow-sm">
            A
          </div>
          <span className="text-xs font-medium text-slate-200">{assignee}</span>
        </div>
      ),
    },
  ];

  return (
    <div className="relative overflow-hidden rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
      {/* Subtle green left accent bar */}
      <div className="absolute inset-y-0 left-0 w-[3px] bg-emerald-500" />

      <div className="space-y-4">
        {metadataItems.map((item, index) => (
          <div
            key={index}
            className="flex items-center justify-between gap-4 text-xs sm:text-sm"
          >
            <span className="font-medium text-slate-400">{item.label}</span>
            {item.customRender ? (
              item.customRender
            ) : (
              <span
                className={`text-right font-medium text-slate-200 ${
                  item.isMono ? 'font-mono text-xs' : ''
                }`}
              >
                {item.value}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default IncidentMetadataCard;
