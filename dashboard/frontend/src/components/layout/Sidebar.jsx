import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  AlertTriangle,
  Shield,
  FileText,
  Settings,
  BookOpen,
  HelpCircle,
  X,
} from 'lucide-react';

const Sidebar = ({ onClose }) => {
  const location = useLocation();

  // ✅ 1. Define menuSections INSIDE the component
  const menuSections = [
    {
      title: 'MONITOR',
      items: [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
        {
          icon: AlertTriangle,
          label: 'Incidents',
          path: '/incidents',
          badge: 2,
        },
      ],
    },
    {
      title: 'GOVERN',
      items: [
        { icon: Shield, label: 'Action Policy', path: '/policy' },
        { icon: FileText, label: 'Audit Log', path: '/audit' },
      ],
    },
    {
      title: 'SYSTEM',
      items: [{ icon: Settings, label: 'Settings', path: '/settings' }],
    },
  ];

  // ✅ 2. Define footerItems
  const footerItems = [
    { icon: BookOpen, label: 'Documentation', path: '/docs' },
    { icon: HelpCircle, label: 'Support', path: '/support' },
  ];

  // ✅ 3. Helper function for active state
  const isActive = (path) => location.pathname === path;

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-800 bg-slate-900">
      {/* Header */}
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

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-2">
        {menuSections.map((section, idx) => (
          <div key={idx} className="mb-5">
            <div className="mb-2 px-3 text-[10px] font-semibold tracking-wider text-slate-500">
              {section.title}
            </div>
            <div className="space-y-0.5">
              {section.items.map((item, itemIdx) => {
                const Icon = item.icon;
                const active = isActive(item.path);
                return (
                  <Link
                    key={itemIdx}
                    to={item.path}
                    onClick={onClose}
                    className={`group flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                      active
                        ? 'bg-slate-800 text-white border-l-2 border-indigo-500'
                        : 'text-slate-400 hover:bg-slate-800/60 hover:text-white'
                    }`}
                  >
                    <Icon
                      className={`h-4 w-4 flex-shrink-0 ${
                        active ? 'text-white' : 'text-slate-500 group-hover:text-white'
                      }`}
                    />
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <span className="flex h-5 min-w-[20px] items-center justify-center rounded-full bg-red-500/20 px-1.5 text-[10px] font-semibold text-red-400">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-800 px-3 py-4">
        <div className="mb-3 flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500"></span>
          </span>
          <span>Cluster Healthy</span>
        </div>
        {footerItems.map((item, idx) => {
          const Icon = item.icon;
          return (
            <a
              key={idx}
              href={item.path}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-400 hover:bg-slate-800/60 hover:text-white transition-colors"
            >
              <Icon className="h-4 w-4 flex-shrink-0" />
              <span>{item.label}</span>
            </a>
          );
        })}
      </div>
    </aside>
  );
};

export default Sidebar;