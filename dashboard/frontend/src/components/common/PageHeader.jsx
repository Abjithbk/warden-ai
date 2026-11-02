import LiveClock from './LiveClock'

const PageHeader = ({ title, subtitle, children }) => (
  <div className="mb-6 flex items-start justify-between gap-4">
    <div>
      <h1 className="text-2xl font-bold text-white">{title}</h1>
      {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
    </div>
    <div className="flex items-center gap-4">
      {children}
      <LiveClock className="text-sm text-slate-500" />
    </div>
  </div>
)

export default PageHeader