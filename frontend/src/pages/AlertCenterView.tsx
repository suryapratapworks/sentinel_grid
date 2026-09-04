import React, { useState } from 'react';
import { ShieldAlert, CheckCircle, Navigation } from 'lucide-react';
import { Alert } from '../types';
import { api } from '../services/api';

interface AlertCenterViewProps {
  alerts: Alert[];
  onRefresh: () => void;
  onInvestigatePlate: (plate: string) => void;
}

export const AlertCenterView: React.FC<AlertCenterViewProps> = ({ alerts, onRefresh, onInvestigatePlate }) => {
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [priorityFilter, setPriorityFilter] = useState('ALL');

  const filteredAlerts = alerts.filter(a => {
    const matchStatus = statusFilter === 'ALL' || a.status === statusFilter;
    const matchPriority = priorityFilter === 'ALL' || a.priority === priorityFilter;
    return matchStatus && matchPriority;
  });

  const handleAcknowledge = async (id: string) => {
    try {
      await api.acknowledgeAlert(id);
      onRefresh();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div className="space-y-4 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-[#111827] p-4 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-rose-400" />
            <h1 className="text-base font-bold text-white tracking-wide">Real-Time Alert Dispatch & Triage</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Automated ANPR Watchlist Hits, High-Priority Incident Alarms & Investigation Links.
          </p>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#0b0f19] border border-slate-700 rounded-lg px-3 py-2 text-slate-300 font-mono focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            <option value="ALL">All Statuses</option>
            <option value="ACTIVE">ACTIVE</option>
            <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-[#0b0f19] border border-slate-700 rounded-lg px-3 py-2 text-slate-300 font-mono focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            <option value="ALL">All Priorities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {filteredAlerts.map((alert) => {
          const isActive = alert.status === 'ACTIVE';
          return (
            <div
              key={alert.id}
              className={`bg-[#111827] border rounded-xl p-4 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl ${
                isActive ? 'border-rose-600/60 bg-gradient-to-r from-[#111827] via-rose-950/10 to-[#111827]' : 'border-slate-800'
              }`}
            >
              <div className="flex items-start space-x-3.5">
                <div className="mt-1">
                  <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-rose-500 animate-ping' : 'bg-slate-600'}`} />
                </div>

                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono font-black text-sm text-white bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                      {alert.plate_number}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-rose-950 text-rose-400 border border-rose-800">
                      {alert.priority}
                    </span>
                    <span className="text-xs text-cyan-400 font-mono font-bold">
                      {alert.watchlist_name}
                    </span>
                  </div>

                  <p className="text-xs text-slate-200 mt-1.5 font-medium">{alert.reason}</p>

                  <div className="flex flex-wrap items-center gap-4 text-[11px] text-slate-400 font-mono mt-1">
                    <span>Camera: <strong className="text-white">{alert.camera_name}</strong></span>
                    <span>Time: {new Date(alert.created_at).toLocaleString()}</span>
                    {alert.acknowledged_by && (
                      <span className="text-emerald-400">Ack by: {alert.acknowledged_by}</span>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2.5 w-full md:w-auto justify-end">
                <button
                  onClick={() => onInvestigatePlate(alert.plate_number)}
                  className="bg-slate-800 hover:bg-slate-700 text-cyan-300 font-bold text-xs px-3.5 py-2 rounded-lg border border-slate-700 transition-all cursor-pointer flex items-center gap-1.5"
                >
                  <Navigation className="w-3.5 h-3.5" />
                  <span>Investigate Route</span>
                </button>

                {isActive ? (
                  <button
                    onClick={() => handleAcknowledge(alert.id)}
                    className="bg-rose-600 hover:bg-rose-500 text-white font-bold text-xs px-3.5 py-2 rounded-lg shadow-lg shadow-rose-600/20 transition-all cursor-pointer flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Acknowledge</span>
                  </button>
                ) : (
                  <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950 px-3 py-1.5 rounded-lg border border-emerald-800/80">
                    ACKNOWLEDGED
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {filteredAlerts.length === 0 && (
          <div className="text-center py-12 bg-[#111827] border border-slate-800 rounded-xl text-xs text-slate-500 font-mono">
            No alerts found matching filter criteria.
          </div>
        )}
      </div>
    </div>
  );
};