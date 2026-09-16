import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import AuditLog from './pages/AuditLog';
import Dashboard from './pages/Dashboard';
import ActionPolicyPage from './pages/ActionPolicyPage';
import IncidentsPage from './pages/IncidentsPage';
import IncidentDetailPage from './pages/IncidentDetailPage';

// Placeholder pages for other routes
const Settings = () => <div className="p-8 text-white"><h1 className="text-2xl font-bold">Settings</h1></div>;

function App() {
  return (
    <Router>
      {/* Layout now owns all routes */}
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/incidents/:id" element={<IncidentDetailPage />} />
          <Route path="/policy" element={<ActionPolicyPage />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;