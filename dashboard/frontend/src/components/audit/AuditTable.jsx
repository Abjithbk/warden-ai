import StatusBadge from '../common/StatusBadge';

const AuditTable = ({ data }) => {
  if (data.length === 0) {
    return (
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-8 text-center">
        <p className="text-sm text-slate-400">No results found</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/50">
      {/* Desktop+ table */}
      <div className="hidden md:block">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-800">
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                Time
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                Incident
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                Service
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                Action
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                Result
              </th>
              <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                Rollback
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {data.map((row, idx) => (
              <tr key={idx} className="transition-colors hover:bg-slate-800/40">
                <td className="px-5 py-3.5 font-mono text-xs text-slate-500">
                  {row.time}
                </td>
                <td className="px-5 py-3.5 text-sm font-semibold text-white">
                  {row.incident}
                </td>
                <td className="px-5 py-3.5 text-sm text-slate-300">
                  {row.service}
                </td>
                <td className="px-5 py-3.5 text-sm text-slate-300">
                  {row.action}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={row.result} />
                </td>
                <td className="px-5 py-3.5 text-sm text-slate-500">
                  {row.rollback}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile card layout */}
      <div className="divide-y divide-slate-800 md:hidden">
        {data.map((row, idx) => (
          <div key={idx} className="p-4">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-semibold text-white">
                {row.incident}
              </span>
              <StatusBadge status={row.result} />
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Time</span>
                <span className="font-mono text-xs text-slate-400">
                  {row.time}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Service</span>
                <span className="text-slate-300">{row.service}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Action</span>
                <span className="text-slate-300">{row.action}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Rollback</span>
                <span className="text-slate-400">{row.rollback}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AuditTable;