import { useState } from 'react';
import PageHeader from '../components/common/PageHeader';

const initialIntegrations = [
  {
    id: 'slack',
    name: 'Slack notifications',
    detail: '#warden-alerts',
    enabled: true,
  },
  {
    id: 'claude',
    name: 'Claude API',
    detail: 'Diagnosis & decision engine',
    enabled: true,
  },
  {
    id: 'launchdarkly',
    name: 'LaunchDarkly',
    detail: 'Feature flag control',
    enabled: true,
  },
];

const clusterDetails = [
  { label: 'Context', value: 'us-east-1-main' },
  { label: 'Prometheus endpoint', value: 'http://prometheus:9090' },
  { label: 'Namespace watched', value: 'production-auth' },
];

const SettingsPage = () => {
  const [integrations, setIntegrations] = useState(initialIntegrations);

  const toggleIntegration = (id) => {
    setIntegrations((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, enabled: !item.enabled } : item
      )
    );
  };

  return (
    <div>
      {/* Reusable PageHeader with live digital clock */}
      <PageHeader
        title="Settings"
        subtitle="Integrations and connection status"
      />

      {/* Settings Grid */}
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 items-start">
        {/* Card 1: INTEGRATIONS */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">
            INTEGRATIONS
          </h2>

          <div className="divide-y divide-slate-800/60">
            {integrations.map((item) => (
              <div
                key={item.id}
                className="flex items-center justify-between py-3.5 first:pt-1 last:pb-1"
              >
                <div>
                  <h3 className="text-sm font-medium text-white">
                    {item.name}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">{item.detail}</p>
                </div>

                {/* Toggle switch */}
                <button
                  type="button"
                  role="switch"
                  aria-checked={item.enabled}
                  onClick={() => toggleIntegration(item.id)}
                  className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 ${
                    item.enabled ? 'bg-emerald-500' : 'bg-slate-700'
                  }`}
                >
                  <span className="sr-only">Toggle {item.name}</span>
                  <span
                    aria-hidden="true"
                    className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm ring-0 transition duration-200 ease-in-out ${item.enabled ? 'translate-x-5' : 'translate-x-0'
                      }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Card 2: CLUSTER CONNECTION */}
        <div className="rounded-xl border border-slate-800/80 bg-slate-900/60 p-5 shadow-lg backdrop-blur-sm">
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">
            CLUSTER CONNECTION
          </h2>

          <div className="divide-y divide-slate-800/60">
            {clusterDetails.map((detail, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between py-3.5 first:pt-1 last:pb-1 text-sm"
              >
                <span className="font-medium text-slate-200">
                  {detail.label}
                </span>
                <span className="font-mono text-xs sm:text-sm text-slate-400">
                  {detail.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
