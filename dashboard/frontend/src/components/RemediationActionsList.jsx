function RemediationActionsList({ actions }) {
  return (
    <div className="bg-slate-900 border border-gray-800 rounded-xl p-5">
      <p className="text-gray-400 text-xs tracking-wide mb-4">RECENT REMEDIATION ACTIONS</p>
      <div className="flex flex-col">
        {actions.map((action, index) => (
          <div
            key={action.id}
            className={`flex items-center justify-between py-3 ${index !== actions.length - 1 ? 'border-b border-gray-800' : ''}`}
          >
            <div className="flex items-start gap-3">
              <span className={`w-2 h-2 rounded-full mt-1.5 ${action.status === 'Resolved' ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
              <div>
                <p className="text-white text-sm font-semibold">{action.title}</p>
                <p className="text-gray-500 text-xs mt-0.5">{action.subtitle}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-1 rounded-full ${action.status === 'Resolved' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'}`}>
                {action.status}
              </span>
              <span className="text-gray-500 text-xs whitespace-nowrap">{action.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default RemediationActionsList