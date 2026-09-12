import { useState } from 'react';
import { RotateCcw, Monitor, Flag, Check } from 'lucide-react';

const icons = {
  RotateCcw: RotateCcw,
  Monitor: Monitor,
  Flag: Flag,
};

function PolicyCard({ icon, title, description, guardrails, enabled }) {
  const Icon = icons[icon];
  const [isEnabled, setIsEnabled] = useState(enabled);

  return (
    <div className="relative rounded-xl border border-slate-800 bg-slate-900 p-6">
      <button
        onClick={() => setIsEnabled(!isEnabled)}
        className={`absolute top-6 right-6 h-3 w-3 rounded-full ${
          isEnabled ? 'opacity-0' : 'bg-slate-950'
        }`}
      />
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-500/10">
          <Icon className="h-5 w-5 text-indigo-400" />
        </div>
        <h3 className="font-bold text-white">{title}</h3>
      </div>
      <p className="mt-4 text-sm text-slate-400">{description}</p>
      <ul className="mt-4 space-y-2">
        {guardrails.map((rule) => (
          <li key={rule} className="flex items-start gap-2 text-sm text-slate-300">
            <Check className="mt-0.5 h-4 w-4 flex-shrink-0 text-emerald-500" />
            {rule}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PolicyCard;