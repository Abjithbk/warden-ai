import { Link, useLocation } from 'react-router-dom'
import { LayoutDashboard, AlertTriangle, Shield, FileText, Settings, X } from 'lucide-react'
import { useOverviewStats } from '../../api/queries'

const MENU_SECTIONS = [
  {
    title: 'MONITOR',
    items: [
      { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
      { icon: AlertTriangle, label: 'Incidents', path: '/incidents', badgeKey: 'active_incidents' },
    ],
  },
  {
    title: 'GOVERN',
    items: [
      { icon: Shield, label: 'Action Policy', path: '/policy' },
      { icon: FileText, label: 'Audit Log', path: '/audit' },
    ],
  },
  { title: 'SYSTEM', items: [{ icon: Settings, label: 'Settings', path: '/settings' }] },
]

const Sidebar = ({ onClose }) => {
  const { pathname } = useLocation()
  const stats = useOverviewStats()

  const isActive = (path) => (path === '/' ? pathname === '/' : pathname.startsWith(path))
  const apiOk = stats.isSuccess
  const apiDown = stats.isError

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-900">
      <div className="flex items-center justify-between px-5 py-5">
        <Link to="/" className="flex items-center gap-3" onClick={onClose}>
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 text-sm font-bold text-white">
            W
          </div>
          <div>
            <div className="text-sm font-semibold text-white">Warden</div>
            <div className="text-xs text-slate-500">AI SRE Co-pilot</div>
          </div>
        </Link>
        <button
          onClick={onClose}
          className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          aria-label="Close menu"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-2">
        {MENU_SECTIONS.map((section) => (
          <div key={section.title} className="mb-5">
            <div className="mb-2 px-3 text-[10px] font-semibold tracking-wider text-slate-500">
              {section.title}
            </div>
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon
                const active = isActive(item.path)
                const badge = item.badgeKey ? stats.data?.[item.badgeKey] : null
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    onClick={onClose}
                    className={`group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${active
                        ? 'border-l-2 border-indigo-500 bg-slate-800 text-white'
                        : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                      }`}
                  >
                    <Icon
                      className={`h-4 w-4 shrink-0 ${active ? 'text-white' : 'text-slate-500 group-hover:text-white'}`}
                    />
                    <span className="flex-1">{item.label}</span>
                    {badge > 0 && (
                      <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-500/20 px-1.5 text-[10px] font-semibold text-red-400">
                        {badge}
                      </span>
                    )}
                  </Link>
                )
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="border-t border-slate-800 px-3 py-4">
        <div className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400">
          <span
            className={`h-2 w-2 rounded-full ${apiOk ? 'bg-emerald-500' : apiDown ? 'bg-rose-500' : 'bg-slate-500'
              }`}
          />
          <span>{apiOk ? 'API connected' : apiDown ? 'API unreachable' : 'Connecting...'}</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar