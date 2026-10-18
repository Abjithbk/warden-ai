import { Siren, Lightbulb, ShieldCheck, UserCheck } from 'lucide-react';

const features = [
  {
    label: 'Incident Detection',
    icon: Siren,
    boxClass: 'border-violet-400 bg-violet-500/10 text-violet-300',
  },
  {
    label: 'AI Reasoning',
    icon: Lightbulb,
    boxClass: 'border-emerald-400 bg-emerald-500/10 text-emerald-300',
  },
  {
    label: 'Policy Guardrails',
    icon: ShieldCheck,
    boxClass: 'border-emerald-400 bg-emerald-500/10 text-emerald-300',
  },
  {
    label: 'Human-in-the-Loop Approval',
    icon: UserCheck,
    boxClass: 'border-emerald-400 bg-emerald-500/10 text-emerald-300',
  },
];

const AuthBranding = () => {
  return (
    <div>
      {/* Logo and product name */}
      <div className="flex items-center gap-4">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-400 to-purple-600 text-3xl font-bold text-white shadow-lg shadow-purple-500/40">
          W
        </div>
        <div>
          <h1 className="text-4xl font-bold text-white">Warden</h1>
          <p className="text-lg text-slate-400">AI SRE Co-pilot</p>
        </div>
      </div>

      {/* Tagline */}
      <p className="mt-6 text-xl text-slate-400">Detect. Reason. Fix. Safely.</p>

      {/* Feature diagram */}
      <div className="mt-12 flex items-center">
        {/* Small W box on the left */}
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-400 to-purple-600 text-2xl font-bold text-white shadow-lg shadow-purple-500/40">
          W
        </div>

        {/* Curved lines from the W box to each feature (SVG = Scalable Vector Graphics) */}
        <svg
          width="70"
          height="240"
          viewBox="0 0 70 240"
          fill="none"
          className="shrink-0"
        >
          <path d="M0 120 C35 120 35 30 70 30" stroke="#a78bfa" strokeWidth="1.5" />
          <path d="M0 120 C35 120 35 90 70 90" stroke="#34d399" strokeWidth="1.5" />
          <path d="M0 120 C35 120 35 150 70 150" stroke="#34d399" strokeWidth="1.5" />
          <path d="M0 120 C35 120 35 210 70 210" stroke="#34d399" strokeWidth="1.5" />
        </svg>

        {/* The four features */}
        <div>
          {features.map(({ label, icon: Icon, boxClass }) => (
            <div key={label} className="flex h-[60px] items-center gap-4">
              <div
                className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border ${boxClass}`}
              >
                <Icon className="h-5 w-5" />
              </div>
              <span className="max-w-[200px] text-lg leading-tight text-white">
                {label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AuthBranding;