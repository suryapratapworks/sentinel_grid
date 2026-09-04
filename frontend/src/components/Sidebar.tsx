import React from 'react';
import {
  LayoutDashboard, Map, Video, Search, ShieldAlert,
  Layers, Lock, Radio, Camera
} from 'lucide-react';

interface SidebarProps {
  activeView: string;
  onSelectView: (view: string) => void;
  alertCount: number;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeView, onSelectView, alertCount }) => {
  const navItems = [
    { id: 'dashboard',   label: 'Command Overview',     icon: LayoutDashboard },
    { id: 'gis',         label: 'GIS Live Map',         icon: Map,         badge: 'LIVE' },
    { id: 'matrix',      label: 'Video Wall Matrix',    icon: Video },
    { id: 'registry',    label: 'Camera Registry',      icon: Camera,      note: 'Model 1' },
    { id: 'investigator',label: 'Vehicle Investigator', icon: Search,      note: 'PTS ANPR' },
    { id: 'alerts',      label: 'Alert Center',         icon: ShieldAlert, badge: alertCount > 0 ? String(alertCount) : undefined, badgeColor: 'bg-rose-500' },
    { id: 'watchlists',  label: 'Watchlists Hotlist',   icon: Radio },
    { id: 'federation',  label: 'Federation Hub',       icon: Layers,      note: 'Model 3' },
    { id: 'evidence',    label: 'Evidence Vault',       icon: Lock,        note: 'Model 4' },
  ];

  return (
    <aside className="w-64 bg-nav border-r border-border flex flex-col justify-between select-none h-[calc(100vh-4rem)] transition-colors duration-300">
      <div className="p-4 space-y-1.5 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-muted font-mono">
          Navigation Matrix
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectView(item.id)}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                isActive
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/40 shadow-sm'
                  : 'text-secondary hover:text-primary hover:bg-surface border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-muted'}`} />
                <span>{item.label}</span>
              </div>
              <div className="flex items-center space-x-1.5">
                {item.note && (
                  <span className="text-[9px] text-muted font-mono font-medium">{item.note}</span>
                )}
                {item.badge && (
                  <span className={`px-1.5 py-0.5 text-[10px] font-bold rounded-full text-white ${item.badgeColor || 'bg-cyan-600'}`}>
                    {item.badge}
                  </span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      <div className="p-4 border-t border-border bg-elevated transition-colors duration-300">
        <div className="rounded-lg bg-surface border border-border p-3 text-[11px] space-y-1.5 transition-colors duration-300">
          <div className="flex justify-between">
            <span className="text-muted">Architecture:</span>
            <span className="text-cyan-400 font-mono font-bold">4-Tier Hybrid</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">RTSP Protocol:</span>
            <span className="text-emerald-400 font-mono font-bold">TCP Forced</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted">Evidence Lock:</span>
            <span className="text-amber-400 font-mono font-bold">SHA-256</span>
          </div>
        </div>
      </div>
    </aside>
  );
};