import React, { useState } from 'react';
import { 
  Camera, ShieldAlert, Car, Layers, 
  CheckCircle, ArrowUpRight, Zap, Radio, Video, Plus
} from 'lucide-react';
import { DashboardStats, Camera as CameraType, Alert, Adapter } from '../types';
import { api } from '../services/api';

interface DashboardViewProps {
  stats: DashboardStats | null;
  cameras: CameraType[];
  alerts: Alert[];
  adapters: Adapter[];
  onSelectView: (view: string) => void;
  onRefresh: () => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  stats, cameras, alerts, adapters, onSelectView, onRefresh
}) => {
  const [processing, setProcessing] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleTestANPR = async () => {
    if (cameras.length === 0) {
      setFeedback('No cameras registered. Please onboard a camera in the Camera Registry first.');
      return;
    }
    setProcessing(true);
    setFeedback(null);
    try {
      const targetCam = cameras[0];
      const testPlates = ['DL-01-AB-1234', 'MH-02-CD-5678', 'HR-26-DK-8899'];
      const plate = testPlates[Math.floor(Math.random() * testPlates.length)];

      const res = await api.simulateLiveANPR({
        camera_id: targetCam.id,
        plate_number: plate,
        confidence: 0.98,
        pts_ms: Date.now(),
        speed_kmh: 48.5,
        vehicle_type: 'SEDAN',
        make_model: 'Patrol Test Vehicle',
        color: 'Silver'
      });

      setFeedback(`ANPR Processed: ${res.plate_number} at ${targetCam.camera_code} ${res.watchlist_match ? '🔥 [HOTLIST HIT]' : '✅ [RECORDED]'}`);
      onRefresh();
    } catch (e: any) {
      setFeedback(`ANPR error: ${e.message}`);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-[#111827] via-[#151e32] to-[#111827] p-5 rounded-xl border border-slate-800 shadow-xl">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <span>Command Center Overview</span>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">
              Statewide Operations Live
            </span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Heterogeneous Statewide CCTV Ingestion, VMS Federation, ANPR Analytics & Selective Evidence Archival.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {cameras.length === 0 ? (
            <button
              onClick={() => onSelectView('registry')}
              className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg shadow-cyan-500/20 transition-all cursor-pointer font-mono"
            >
              <Plus className="w-4 h-4" />
              <span>Onboard First Camera</span>
            </button>
          ) : (
            <button
              onClick={handleTestANPR}
              disabled={processing}
              className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg shadow-cyan-500/20 transition-all cursor-pointer disabled:opacity-50 font-mono"
            >
              <Zap className={`w-4 h-4 ${processing ? 'animate-spin' : ''}`} />
              <span>{processing ? 'Processing ANPR...' : 'Test ANPR Detection'}</span>
            </button>
          )}
        </div>
      </div>

      {feedback && (
        <div className="bg-slate-900/90 border border-cyan-500/40 p-3 rounded-lg text-xs font-mono flex items-center justify-between text-cyan-300">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span>{feedback}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-slate-500 hover:text-white">&times;</button>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div 
          onClick={() => onSelectView('registry')}
          className="bg-surface border border-border hover:border-cyan-500/50 p-4 rounded-xl transition-all cursor-pointer shadow-sm group"
        >
          <div className="flex items-center justify-between text-muted text-xs font-semibold">
            <span>STATEWIDE CAMERAS</span>
            <Camera className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-primary font-mono">{stats?.total_cameras ?? 0}</span>
            <span className="text-[11px] text-emerald-400 flex items-center font-bold">
              <CheckCircle className="w-3 h-3 mr-1" /> {stats?.online_cameras ?? 0} Online
            </span>
          </div>
          <div className="mt-2 w-full bg-base rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full" 
              style={{ width: `${stats && stats.total_cameras > 0 ? (stats.online_cameras / stats.total_cameras) * 100 : 0}%` }}
            />
          </div>
        </div>

        <div 
          onClick={() => onSelectView('alerts')}
          className="bg-surface border border-border hover:border-rose-500/50 p-4 rounded-xl transition-all cursor-pointer shadow-sm group"
        >
          <div className="flex items-center justify-between text-muted text-xs font-semibold">
            <span>CRITICAL ALERTS</span>
            <ShieldAlert className="w-4 h-4 text-rose-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-rose-400 font-mono">{stats?.active_alerts ?? 0}</span>
            <span className="text-[11px] text-rose-300 font-bold uppercase tracking-wider">
              {stats?.watchlist_hits ?? 0} Watchlist Hits
            </span>
          </div>
          <div className="mt-2 text-[10px] text-muted font-mono">
            {stats && stats.active_alerts > 0 ? 'Immediate triage required' : 'All sectors clear'}
          </div>
        </div>

        <div 
          onClick={() => onSelectView('investigator')}
          className="bg-surface border border-border hover:border-amber-500/50 p-4 rounded-xl transition-all cursor-pointer shadow-sm group"
        >
          <div className="flex items-center justify-between text-muted text-xs font-semibold">
            <span>UNIQUE VEHICLES</span>
            <Car className="w-4 h-4 text-amber-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-primary font-mono">{stats?.total_vehicles_detected ?? 0}</span>
            <span className="text-[11px] text-amber-400 font-bold">PTS Correlated</span>
          </div>
          <div className="mt-2 text-[10px] text-muted font-mono">ANPR Cross-Camera Track</div>
        </div>

        <div 
          onClick={() => onSelectView('federation')}
          className="bg-surface border border-border hover:border-cyan-500/50 p-4 rounded-xl transition-all cursor-pointer shadow-sm group"
        >
          <div className="flex items-center justify-between text-muted text-xs font-semibold">
            <span>FEDERATION ADAPTERS</span>
            <Layers className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-primary font-mono">{stats?.total_adapters ?? 4} Active</span>
            <span className="text-[11px] text-emerald-400 font-bold">{stats?.system_health_score ?? 100}% Health</span>
          </div>
          <div className="mt-2 text-[10px] text-muted font-mono">RTSP, ONVIF, VMS Bridges</div>
        </div>
      </div>

      {/* Main Grid: Alerts & Adapters */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-5 shadow-xl">
          <div className="flex items-center justify-between pb-3 border-b border-border">
            <div className="flex items-center space-x-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              <h2 className="text-sm font-bold text-primary tracking-wide">Real-Time Threat Alerts</h2>
            </div>
            <button 
              onClick={() => onSelectView('alerts')} 
              className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 cursor-pointer font-mono"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="mt-4 space-y-3">
            {alerts.slice(0, 4).map((alert) => (
              <div 
                key={alert.id}
                className="bg-base border border-border hover:border-rose-500/40 p-3.5 rounded-lg flex items-center justify-between transition-all"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-primary text-sm bg-surface px-2 py-0.5 rounded border border-border">
                        {alert.plate_number}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
                        {alert.priority}
                      </span>
                    </div>
                    <p className="text-xs text-primary mt-1 font-medium">{alert.reason}</p>
                    <p className="text-[10px] text-muted font-mono mt-0.5">Location: {alert.camera_name}</p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[11px] font-mono text-muted block">
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </span>
                  <button
                    onClick={() => onSelectView('investigator')}
                    className="mt-1 text-[11px] text-cyan-400 hover:text-cyan-300 font-bold underline cursor-pointer font-mono"
                  >
                    Track Route →
                  </button>
                </div>
              </div>
            ))}

            {alerts.length === 0 && (
              <div className="text-center py-8 text-xs text-muted font-mono">
                No active critical alerts. All monitored corridors secure.
              </div>
            )}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-border">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-cyan-400" />
                <h2 className="text-sm font-bold text-primary tracking-wide">Federation Middleware</h2>
              </div>
              <span className="text-[10px] font-bold text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30">
                MODEL 3 READY
              </span>
            </div>

            <div className="mt-4 space-y-3">
              {adapters.map((ad) => (
                <div key={ad.id} className="p-3 rounded-lg bg-base border border-border space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-primary">{ad.name}</span>
                    <span className="text-[10px] font-bold font-mono text-cyan-400 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/30">
                      {ad.adapter_type}
                    </span>
                  </div>
                  <div className="flex justify-between text-[11px] text-muted font-mono">
                    <span>Vendor: {ad.vendor}</span>
                    <span className="text-emerald-400 font-bold">{ad.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-border text-[11px] text-muted">
            <div className="flex justify-between">
              <span>Selective Evidence Storage:</span>
              <span className="text-cyan-400 font-bold font-mono">Model 4 Active</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};