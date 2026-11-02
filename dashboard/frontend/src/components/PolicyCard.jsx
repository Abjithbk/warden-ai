import { RotateCcw, Monitor, Flag, Check } from 'lucide-react'

const ICONS = { RotateCcw, Monitor, Flag }

function PolicyCard({ icon, title, description, guardrails, enabled }) {
  const Icon = ICONS[icon] ?? Flag

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10">
            <Icon className="h-5 w-5 text-indigo-400" />
          </div>
          <h3 className="font-bold text-white">{title}</h3>
        </div>
        <span
          className={`rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${enabled
              ? 'border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
              : 'border-slate-500/30 bg-slate-500/15 text-slate-400'
            }`}
        >
          {enabled ? 'Allowed' : 'Planned'}
        </span>
      </div>
      <p className="mt-4 text-sm text-slate-400">{description}</p>
      <ul className="mt-4 space-y-2">
        {guardrails.map((rule) => (
          <li key={rule} className="flex items-start gap-2 text-sm text-slate-300">
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
            {rule}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default PolicyCard