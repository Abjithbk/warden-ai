import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Layout from './components/layout/Layout'
import AuditLog from './pages/AuditLog'
import Dashboard from './pages/Dashboard'
import ActionPolicyPage from './pages/ActionPolicyPage'
import IncidentsPage from './pages/IncidentsPage'
import IncidentDetailPage from './pages/IncidentDetailPage'
import SettingsPage from './pages/SettingsPage'

const NotFound = () => (
  <p className="py-16 text-center text-sm text-slate-400">Page not found.</p>
)

// SignInPage / ActivateAccountPage are left out of the routes until the
// backend has real authentication.
export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="incidents" element={<IncidentsPage />} />
          <Route path="incidents/:id" element={<IncidentDetailPage />} />
          <Route path="audit" element={<AuditLog />} />
          <Route path="policy" element={<ActionPolicyPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}