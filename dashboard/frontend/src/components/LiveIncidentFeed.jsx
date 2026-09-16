import { Link } from 'react-router-dom';

function LiveIncidentFeed({ incidents }) {
  return (
    <div className="bg-slate-900 border border-gray-800 rounded-xl p-5">
      <p className="text-gray-400 text-xs tracking-wide mb-4">LIVE INCIDENT FEED</p>
      <div className="flex flex-col">
        {incidents.map((incident, index) => {
          const targetId = incident.id === 1 ? 'inc-001' : incident.id;
          return (
            <Link
              key={incident.id}
              to={`/incidents/${targetId}`}
              className={`group flex items-center justify-between py-3 transition-colors hover:bg-slate-800/40 px-2 rounded-lg -mx-2 ${
                index !== incidents.length - 1 ? 'border-b border-gray-800' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <span
                  className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                    incident.status === 'Awaiting Approval'
                      ? 'bg-indigo-400'
                      : 'bg-amber-400'
                  }`}
                ></span>
                <div>
                  <p className="text-white text-sm font-semibold group-hover:text-indigo-300 transition-colors">
                    {incident.title}
                  </p>
                  <p className="text-gray-500 text-xs mt-0.5">{incident.subtitle}</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span
                  className={`text-xs px-2.5 py-1 rounded-full whitespace-nowrap ${
                    incident.status === 'Awaiting Approval'
                      ? 'bg-indigo-950 text-indigo-400 border border-indigo-500/30'
                      : 'bg-amber-950 text-amber-400 border border-amber-500/30'
                  }`}
                >
                  {incident.status}
                </span>
                <span className="text-gray-500 text-xs whitespace-nowrap">
                  {incident.time}
                </span>
              </div>
            </Link>
          );
        })}
      </div>
      <Link to="/incidents" className="text-indigo-400 text-sm mt-5 inline-block hover:underline">
        View all incidents →
      </Link>
    </div>
  );
}

export default LiveIncidentFeed