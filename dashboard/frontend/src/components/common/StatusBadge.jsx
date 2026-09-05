const StatusBadge = ({status}) => {
    const styles = {
    Pending: 'bg-indigo-500/15 text-indigo-400 border-indigo-500/30',
    'In progress': 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    Success: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    Failed: 'bg-red-500/15 text-red-400 border-red-500/30',
  };

  const style = styles[status] || 'bg-slate-500/15 text-slate-400 border-slate-500/30';

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${style}`}>
      {status}
    </span>
  )
}

export default StatusBadge
