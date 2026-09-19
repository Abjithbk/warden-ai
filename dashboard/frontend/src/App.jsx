import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import AuditLog from './pages/AuditLog';

// Placeholder pages for other routes
const Dashboard = () => <div className="p-8 text-white"><h1 className="text-2xl font-bold">Dashboard</h1></div>;
const Incidents = () => <div className="p-8 text-white"><h1 className="text-2xl font-bold">Incidents</h1></div>;
const Policy = () => <div className="p-8 text-white"><h1 className="text-2xl font-bold">Action Policy</h1></div>;
const Settings = () => <div className="p-8 text-white"><h1 className="text-2xl font-bold">Settings</h1></div>;

function App() {
  return (
    <Router>
      {/* Layout now owns all routes */}
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/audit" element={<AuditLog />} />
          <Route path="/incidents" element={<Incidents />} />
          <Route path="/policy" element={<Policy />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;