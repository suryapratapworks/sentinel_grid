import React from 'react';
import { RefreshCw, Shield, Sun, Moon, LogOut, UserCheck } from 'lucide-react';
import { DashboardStats, AuthUser } from '../types';

interface NavbarProps {
  stats: DashboardStats | null;
  activeView: string;
  onRefresh: () => void;
  onSelectView: (view: string) => void;
  isDark: boolean;
  onToggleTheme: () => void;
  currentUser: AuthUser | null;
  onLogout: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ 
  stats, onRefresh, isDark, onToggleTheme, currentUser, onLogout 
}) => {
  const [clock, setClock] = React.useState(new Date());

  React.useEffect(() => {
    const timer = setInterval(() => setClock(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const pts = clock.getTime();

  return (
    <header className="h-16 bg-nav border-b border-nav flex items-center justify-between px-6 z-50 relative flex-shrink-0">
      <div className="flex items-center space-x-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-sm font-black tracking-widest text-cyan-400 uppercase">
            SENTINEL GRID
          </h1>
          <p className="text-[10px] font-mono text-muted leading-none">
            Unified Federated Video Intelligence Platform
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-4 text-xs font-mono">
        {stats && (
          <div className="hidden md:flex items-center space-x-4 text-muted">
            <span>
              <span className="text-emerald-400 font-bold">{stats.online_cameras}</span>
              <span className="text-muted">/{stats.total_cameras} CAM</span>
            </span>
            <span className="text-border">|</span>
            <span>
              <span className="text-rose-400 font-bold">{stats.active_alerts}</span>
              <span className="text-muted"> ALERTS</span>
            </span>
            <span className="text-border">|</span>
            <span>
              <span className="text-cyan-400 font-bold">{stats.system_health_score}%</span>
              <span className="text-muted"> HEALTH</span>
            </span>
          </div>
        )}

        <div className="hidden md:block text-right">
          <div className="text-primary font-bold text-xs">{clock.toLocaleTimeString()}</div>
          <div className="text-[10px] text-muted">PTS: {pts.toLocaleString()}</div>
        </div>

        {currentUser && (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-surface border border-border">
            <UserCheck className="w-3.5 h-3.5 text-cyan-400" />
            <div className="text-left">
              <div className="text-[10px] font-bold text-primary leading-tight uppercase">
                {currentUser.username}
              </div>
              <div className="text-[9px] text-cyan-400 font-mono leading-tight">
                {currentUser.role}
              </div>
            </div>
            <button
              onClick={onLogout}
              className="ml-1.5 p-1 rounded hover:bg-elevated text-muted hover:text-rose-400 transition-colors cursor-pointer"
              title="Sign Out / Change Identity"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        <button
          onClick={onRefresh}
          className="p-2 rounded-lg hover:bg-surface text-muted hover:text-cyan-400 transition-all cursor-pointer"
          title="Refresh all data"
        >
          <RefreshCw className="w-4 h-4" />
        </button>

        <button
          onClick={onToggleTheme}
          className="p-2 rounded-lg hover:bg-surface transition-all cursor-pointer border border-border flex items-center gap-1.5"
          title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDark ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-cyan-400" />
          )}
          <span className="text-[10px] font-bold hidden md:block text-muted">
            {isDark ? 'Light' : 'Dark'}
          </span>
        </button>
      </div>
    </header>
  );
};