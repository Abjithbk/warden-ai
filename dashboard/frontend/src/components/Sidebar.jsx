const incidentCount = 2

function Sidebar() {
  return (
    <div className="min-h-screen w-64 bg-black text-white p-4 flex flex-col justify-between">
      <div>
        <h1 className="text-xl font-bold">Warden</h1>
        <p className="text-sm text-gray-400 mb-6">AI SRE Co-pilot</p>

        <p className="text-xs text-gray-500 mb-2">MONITOR</p>
        <p className="mb-1 bg-indigo-600/20 text-indigo-400 px-2 py-1 rounded">Dashboard</p>
        <p className="mb-4 flex justify-between px-2">
          <span>Incidents</span>
          <span className="bg-gray-700 text-xs px-2 rounded-full">{incidentCount}</span>
        </p>

        <p className="text-xs text-gray-500 mb-2">GOVERN</p>
        <p className="mb-1 px-2">Action Policy</p>
        <p className="mb-4 px-2">Audit Log</p>

        <p className="text-xs text-gray-500 mb-2">SYSTEM</p>
        <p className="mb-1 px-2">Settings</p>
      </div>

      <div className="text-sm text-gray-400 space-y-2">
        <p className="flex items-center gap-2">
          <span className="w-2 h-2 bg-green-500 rounded-full"></span>
          Cluster Healthy
        </p>
        <p>Documentation</p>
        <p>Support</p>
      </div>
    </div>
  )
}

export default Sidebar