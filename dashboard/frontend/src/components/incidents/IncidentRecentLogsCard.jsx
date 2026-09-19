import { Terminal } from 'lucide-react';

const mockLogs = [
  {
    time: '10:42:01',
    level: 'ERROR',
    message: 'Connection timeout fetching user profile',
  },
  {
    time: '10:42:02',
    level: 'WARN',
    message: 'Memory usage exceeded 90% threshold',
  },
  {
    time: '10:42:04',
    level: 'FATAL',
    message: 'OutOfMemoryError: Java heap space',
  },
  {
    time: '10:42:05',
    level: 'INFO',
    message: 'Container killed by OOMKiller',
  },
  {
    time: '10:42:15',
    level: 'INFO',
    message: 'Starting auth-service-v2...',
  },
];

const levelColorMap = {
  ERROR: 'text-rose-400',
  WARN: 'text-amber-400',
  FATAL: 'text-red-500 font-bold',
  INFO: 'text-sky-400',
};

const IncidentRecentLogsCard = ({ logs = mockLogs }) => {
  return (
    <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded border border-sky-500/40 bg-sky-500/10 text-sky-400">
            <Terminal className="h-3.5 w-3.5" />
          </div>
          <h3 className="text-sm font-semibold text-white">Recent Logs</h3>
        </div>
        <span className="font-mono text-xs text-slate-500">tail -n 5</span>
      </div>

      {/* Log lines */}
      <div className="space-y-3 font-mono text-xs leading-relaxed">
        {logs.map((log) => (
          <div
            key={log.id ?? `${log.time}-${log.level}-${log.message}`}
            className="flex items-baseline gap-2"
          >
            <span className="text-slate-500 flex-shrink-0">{log.time}</span>
            <span
              className={`flex-shrink-0 font-medium ${
                levelColorMap[log.level] || 'text-slate-400'
              }`}
            >
              [{log.level}]
            </span>
            <span className="text-slate-300 break-words">{log.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IncidentRecentLogsCard;
