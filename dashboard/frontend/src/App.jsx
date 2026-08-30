import Sidebar from './components/Sidebar'
import Header from './components/Header'

function App() {
  return (
    <div style={{ display: 'flex' }}>
      <Sidebar />
      <div style={{ flex: 1 }}>
        <Header />
      </div>
    </div>
  )
}

export default App