import React, { useState } from 'react';
import { Shield, Lock, User, Key, ArrowRight, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import { AuthUser } from '../types';

interface LoginViewProps {
  onLoginSuccess: (user: AuthUser) => void;
}

export const LoginView: React.FC<LoginViewProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError('Please enter both username and password.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const user = await api.login(username, password);
      localStorage.setItem('sentinel_token', user.access_token);
      localStorage.setItem('sentinel_user', JSON.stringify(user));
      onLoginSuccess(user);
    } catch (err: any) {
      setError(err.message || 'Invalid credentials. Please verify username and password.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async (u: string, p: string) => {
    setUsername(u);
    setPassword(p);
    setLoading(true);
    setError(null);
    try {
      const user = await api.login(u, p);
      localStorage.setItem('sentinel_token', user.access_token);
      localStorage.setItem('sentinel_user', JSON.stringify(user));
      onLoginSuccess(user);
    } catch (err: any) {
      setError(err.message || 'Quick login failed');
    } finally {
      setLoading(false);
    }
  };

  const demoAccounts = [
    {
      roleName: 'SUPER_ADMIN',
      title: 'State Homeland & Command',
      dept: 'HPS',
      user: 'admin',
      pass: 'admin123',
      badgeColor: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
      tag: 'Full Authority',
    },
    {
      roleName: 'POLICE_OPERATOR',
      title: 'Police Crime & ANPR',
      dept: 'TPD',
      user: 'investigator',
      pass: 'investigator123',
      badgeColor: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
      tag: 'Hotlist & Routing',
    },
    {
      roleName: 'TRAFFIC_OPERATOR',
      title: 'State Traffic Control',
      dept: 'TPD',
      user: 'operator',
      pass: 'operator123',
      badgeColor: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      tag: 'Matrix & Alerts',
    },
    {
      roleName: 'MUNICIPAL_VIEWER',
      title: 'Smart City Operations',
      dept: 'SMC',
      user: 'municipal_viewer',
      pass: 'viewer123',
      badgeColor: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
      tag: 'GIS & Inventory',
    },
  ];

  return (
    <div className="min-h-screen bg-[#0b0f19] flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background tactical grid glow */}
      <div className="absolute inset-0 bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] opacity-25" />
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-4xl relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-6 bg-[#111827]/90 backdrop-blur-xl border border-slate-800 rounded-2xl shadow-2xl p-6 lg:p-8">
        {/* Left Column: Platform Branding & Mission Info */}
        <div className="lg:col-span-6 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-slate-800 pb-6 lg:pb-0 lg:pr-8">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-black tracking-widest text-cyan-400 uppercase font-mono">
                  SENTINEL GRID
                </h1>
                <p className="text-[10px] font-mono text-slate-400 uppercase">
                  Federated Video Intelligence
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed mb-6 font-mono">
              Restricted statewide operational network. Access is logged and subject to cryptographic verification under Model 4 auditing standards.
            </p>

            <div className="space-y-2 mb-6">
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider font-mono">
                Federated Security Protocols
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-300 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>RTSP/TCP Enforced with PTS Verification</span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-300 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>SHA-256 Cryptographic Evidence Vault</span>
              </div>
              <div className="flex items-center space-x-2 text-xs text-slate-300 font-mono">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                <span>PostGIS 3.5 Geospatial Geofence Tracking</span>
              </div>
            </div>
          </div>

          <div className="text-[10px] text-slate-500 font-mono border-t border-slate-800/80 pt-3 flex justify-between">
            <span>SEC-LEVEL: RESTRICTED</span>
            <span>NODE: CENTRAL-01</span>
          </div>
        </div>

        {/* Right Column: Authentication Form & Quick Role Access */}
        <div className="lg:col-span-6 flex flex-col justify-center space-y-5">
          <div>
            <h2 className="text-base font-bold text-white font-mono flex items-center gap-2">
              <Lock className="w-4 h-4 text-cyan-400" />
              Operator Authentication
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Enter official credentials or select role identity
            </p>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-mono flex items-start gap-2">
              <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div>
              <label className="block text-[11px] font-mono font-medium text-slate-300 mb-1">
                Username / Officer ID
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. admin, investigator"
                  className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-[11px] font-mono font-medium text-slate-300 mb-1">
                Password / Secure Passcode
              </label>
              <div className="relative">
                <Key className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono transition-colors"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold font-mono tracking-wider uppercase transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {loading ? (
                <span>Authenticating with Node...</span>
              ) : (
                <>
                  <span>Sign In to Terminal</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Quick Role Selectors for Evaluation */}
          <div className="border-t border-slate-800 pt-3">
            <div className="text-[10px] uppercase font-bold text-slate-400 tracking-wider font-mono mb-2">
              Quick Role-Based Access (Demo Profiles)
            </div>
            <div className="grid grid-cols-2 gap-2">
              {demoAccounts.map((account) => (
                <button
                  key={account.user}
                  type="button"
                  onClick={() => handleQuickLogin(account.user, account.pass)}
                  disabled={loading}
                  className={`p-2 rounded-lg border text-left transition-all hover:scale-[1.02] cursor-pointer ${account.badgeColor}`}
                >
                  <div className="flex justify-between items-center text-[10px] font-mono font-bold">
                    <span>{account.dept}</span>
                    <span className="opacity-80 text-[9px]">{account.tag}</span>
                  </div>
                  <div className="text-xs font-bold text-white mt-0.5 truncate">{account.title}</div>
                  <div className="text-[9px] font-mono text-slate-400 mt-0.5">ID: {account.user}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};