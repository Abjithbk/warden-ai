function LiveIncidentFeed({ incidents }) {
  return (
    <div className="bg-slate-900 border border-gray-800 rounded-xl p-5">
      <p className="text-gray-400 text-xs tracking-wide mb-4">LIVE INCIDENT FEED</p>
      <div className="flex flex-col">
        {incidents.map((incident, index) => (
          <div
            key={incident.id}
            className={`flex items-center justify-between py-3 ${index !== incidents.length - 1 ? 'border-b border-gray-800' : ''}`}
          >
            <div className="flex items-start gap-3">
              <span className={`w-2 h-2 rounded-full mt-1.5 ${incident.status === 'Awaiting Approval' ? 'bg-indigo-400' : 'bg-amber-400'}`}></span>
              <div>
                <p className="text-white text-sm font-semibold">{incident.title}</p>
                <p className="text-gray-500 text-xs mt-0.5">{incident.subtitle}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs px-2 py-1 rounded-full whitespace-nowrap ${incident.status === 'Awaiting Approval' ? 'bg-indigo-950 text-indigo-400' : 'bg-amber-950 text-amber-400'}`}>
                {incident.status}
              </span>
              <span className="text-gray-500 text-xs whitespace-nowrap">{incident.time}</span>
            </div>
          </div>
        ))}
      </div>
      <a href="#" className="text-indigo-400 text-sm mt-5 inline-block">View all incidents →</a>
    </div>
  )
}

export default LiveIncidentFeed