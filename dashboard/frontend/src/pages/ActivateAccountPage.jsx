import { useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Mail, Lock, Eye, EyeOff, Shield, ChevronDown } from 'lucide-react';
import AuthBranding from '../components/auth/AuthBranding';

const inputClass =
  'w-full rounded-xl border border-slate-700 bg-slate-950 py-3 pl-11 pr-11 text-white placeholder-slate-500 outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/40';

// The four user roles of Warden
const roles = ['Site Reliability Engineer', 'Approver', 'Administrator', 'Stakeholder'];

const ActivateAccountPage = () => {
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [role, setRole] = useState('');

  // This email will come from the invite later. For now it is a fixed sample value.
  const workEmail = 'you@company.com';

  const handleSubmit = (e) => {
    e.preventDefault();
    // The backend (server) connection will be added later
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-10">
      <div className="grid w-full max-w-6xl items-center gap-12 lg:grid-cols-2">
        {/* Left side: branding (hidden on small screens) */}
        <div className="hidden lg:block lg:pl-12">
          <AuthBranding />
        </div>

        {/* Right side: activate account card */}
        <div className="mx-auto w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl">
          <h2 className="text-3xl font-bold text-white">Welcome</h2>

          <form onSubmit={handleSubmit} className="mt-6 space-y-5">
            {/* Full name */}
            <div>
              <label htmlFor="fullName" className="mb-2 block text-sm text-white">
                Full name
              </label>
              <div className="relative">
                <User className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Your full name"
                  className={inputClass}
                />
              </div>
            </div>

            {/* Work email (locked, cannot be edited) */}
            <div>
              <label htmlFor="workEmail" className="mb-2 block text-sm text-white">
                Work email
              </label>
              <div className="relative">
                <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <input
                  id="workEmail"
                  type="email"
                  value={workEmail}
                  readOnly
                  className="w-full cursor-not-allowed rounded-xl border border-dashed border-slate-600 bg-slate-950 py-3 pl-11 pr-11 text-slate-300 outline-none"
                />
                <Lock className="pointer-events-none absolute right-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              </div>
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="mb-2 block text-sm text-white">
                Password
              </label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a password"
                  className={inputClass}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <Eye className="h-5 w-5" />
                  ) : (
                    <EyeOff className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Role */}
            <div>
              <label htmlFor="role" className="mb-2 block text-sm text-white">
                Role
              </label>
              <div className="relative">
                <Shield className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
                <select
                  id="role"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  className={`w-full appearance-none rounded-xl border border-slate-700 bg-slate-950 py-3 pl-11 pr-11 outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/40 ${
                    role === '' ? 'text-slate-500' : 'text-white'
                  }`}
                >
                  <option value="" disabled>
                    Select your role
                  </option>
                  {roles.map((r) => (
                    <option key={r} value={r} className="bg-slate-900 text-white">
                      {r}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
              </div>
            </div>

            {/* Activate account button */}
            <button
              type="submit"
              className="w-full rounded-xl bg-violet-600 py-3 font-semibold text-white shadow-lg shadow-violet-600/30 transition-colors hover:bg-violet-500"
            >
              Activate account
            </button>
          </form>

          <p className="mt-5 text-center text-sm text-white">
            Already activated?{' '}
            <Link to="/signin" className="text-violet-300 hover:text-violet-200">
              Sign in
            </Link>
          </p>

          <p className="mt-3 text-center text-sm text-slate-400">
            Protected by policy guardrails and human approval.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ActivateAccountPage;