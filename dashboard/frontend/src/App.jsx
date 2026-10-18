import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import AuditLog from './pages/AuditLog';
import Dashboard from './pages/Dashboard';
import ActionPolicyPage from './pages/ActionPolicyPage';
import IncidentsPage from './pages/IncidentsPage';
import IncidentDetailPage from './pages/IncidentDetailPage';
import SettingsPage from './pages/SettingsPage';
import SignInPage from './pages/SignInPage';
import ActivateAccountPage from './pages/ActivateAccountPage';

function App() {
  return (
    <Router>
      <Routes>
        {/* Login pages: no sidebar, so they sit outside Layout */}
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/activate" element={<ActivateAccountPage />} />

        {/* All other pages: inside Layout (sidebar and top bar) */}
        <Route
          path="/*"
          element={
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/audit" element={<AuditLog />} />
                <Route path="/incidents" element={<IncidentsPage />} />
                <Route path="/incidents/:id" element={<IncidentDetailPage />} />
                <Route path="/policy" element={<ActionPolicyPage />} />
                <Route path="/settings" element={<SettingsPage />} />
              </Routes>
            </Layout>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;