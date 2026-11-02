import PageHeader from '../components/common/PageHeader'
import SlackIntegrationCard from '../components/settings/SlackIntegrationCard'

// The earlier "Claude API" toggle and the hardcoded cluster block were removed:
// they were not connected to anything. Re-add real status cards when the
// agent (M4) and the cluster connection report their own status.
const SettingsPage = () => (
  <div>
    <PageHeader title="Settings" subtitle="Integrations and connection status" />
    <div className="grid grid-cols-1 items-start gap-5 md:grid-cols-2">
      <SlackIntegrationCard />
    </div>
  </div>
)

export default SettingsPage