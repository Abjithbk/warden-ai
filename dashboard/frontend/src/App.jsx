import Sidebar from './components/Sidebar'
import Header from './components/Header'
import StatCard from './components/StatCard'

function App() {
  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <div style={{ flex: 1 }}>
        <Header />
        <div className="flex gap-4 p-6">
          <StatCard value="2" label="Active incidents" subtext="+1 vs yesterday" accentColor="red" />
          <StatCard value="11" label="Auto-resolved today" subtext="92% success rate" accentColor="green" />
          <StatCard value="1m 48s" label="Avg. time to remediate" subtext="steady" accentColor="white" />
          <StatCard value="17" label="Actions taken (24h)" subtext="4 rollbacks" accentColor="white" />
        </div>
      </div>
    </div>
  )
}

export default App