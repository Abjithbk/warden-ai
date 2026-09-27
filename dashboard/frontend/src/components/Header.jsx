import { useState, useEffect } from 'react'

function Header() {
  const clusterStatus = "Degraded"
  const activeIncidentCount = 2

  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="bg-black px-8 py-6 border-b border-gray-800 flex items-center justify-between">
      <div>
        <h1 className="text-white text-2xl font-bold">Overview</h1>
        <p className="text-gray-400 text-sm">Live status of us-east-1-main</p>
      </div>
      <div className="flex items-center gap-4">
        <span className="bg-emerald-950 text-emerald-400 text-sm px-3 py-1 rounded-full border border-emerald-800 flex items-center gap-2">
          <span className="w-2 h-2 bg-emerald-400 rounded-full"></span>
          {clusterStatus} — {activeIncidentCount} active
        </span>
        <span className="text-gray-400 text-sm">
          {currentTime.toLocaleTimeString('en-GB')}
        </span>
      </div>
    </div>
  )
}

export default Header