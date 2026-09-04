import { LayoutGrid, TriangleAlert, Shield, FileText, Settings as SettingsIcon, BookOpen, HelpCircle } from 'lucide-react'

const incidentCount = 2

function Sidebar() {
  return (
    <div className="min-h-screen w-64 bg-[#0d1017] text-white p-4 flex flex-col justify-between border-r border-gray-800">
      <div>
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center font-bold">
            W
          </div>
          <div>
            <h1 className="text-lg font-bold leading-tight">Warden</h1>
            <p className="text-xs text-gray-400 leading-tight">AI SRE Co-pilot</p>
          </div>
        </div>

        <p className="text-xs text-gray-500 mb-2">MONITOR</p>
        <p className="mb-1 bg-indigo-600/20 text-indigo-400 px-2 py-1 rounded flex items-center gap-2">
          <LayoutGrid size={16} />
          Dashboard
        </p>
        <p className="mb-4 flex items-center justify-between px-2">
          <span className="flex items-center gap-2">
            <TriangleAlert size={16} />
            Incidents
          </span>
          <span className="bg-gray-700 text-red-400 text-xs w-4 h-4 rounded-full flex items-center justify-center">
            {incidentCount}
          </span>
        </p>

        <p className="text-xs text-gray-500 mb-2">GOVERN</p>
        <p className="mb-1 px-2 flex items-center gap-2">
          <Shield size={16} />
          Action Policy
        </p>
        <p className="mb-4 px-2 flex items-center gap-2">
          <FileText size={16} />
          Audit Log
        </p>

        <p className="text-xs text-gray-500 mb-2">SYSTEM</p>
        <p className="mb-1 px-2 flex items-center gap-2">
          <SettingsIcon size={16} />
          Settings
        </p>
      </div>

      <div className="text-sm text-gray-400 space-y-2">
        <div className="border-t border-gray-800 pt-3">
          <p className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Cluster Healthy
          </p>
        </div>
        <p className="flex items-center gap-2">
          <BookOpen size={16} />
          Documentation
        </p>
        <p className="flex items-center gap-2">
          <HelpCircle size={16} />
          Support
        </p>
      </div>
    </div>
  )
}

export default Sidebar