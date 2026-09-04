import React from 'react';
import { Layers, Cpu, Server, Activity, ShieldCheck, CheckCircle, Radio } from 'lucide-react';
import { Adapter } from '../types';

interface FederationHubViewProps {
  adapters: Adapter[];
  onRefresh: () => void;
}

export const FederationHubView: React.FC<FederationHubViewProps> = ({ adapters }) => {
  return (
    <div className="space-y-4 pb-12">
      <div className="bg-[#111827] p-5 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2">
          <Layers className="w-5 h-5 text-cyan-400" />
          <div>
            <h1 className="text-base font-bold text-white tracking-wide">Model 3 — Multi-Vendor VMS Federation Middleware</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Modular adapter bridge normalizing proprietary VMS SDKs, ONVIF discovery, and direct RTSP feeds into canonical schemas.
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {adapters.map((ad) => (
          <div key={ad.id} className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h2 className="text-sm font-bold text-white tracking-wide">{ad.name}</h2>
                <p className="text-[11px] text-slate-400 font-mono">Vendor: {ad.vendor} • v{ad.version}</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                {ad.status}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
              <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800/80">
                <span className="text-slate-400 block text-[10px]">ADAPTER TYPE</span>
                <span className="text-cyan-400 font-bold text-sm">{ad.adapter_type}</span>
              </div>

              <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800/80">
                <span className="text-slate-400 block text-[10px]">EVENT THROUGHPUT</span>
                <span className="text-emerald-400 font-bold text-sm">{ad.event_throughput_fps} FPS</span>
              </div>
            </div>

            <div className="bg-[#0b0f19] p-3 rounded-lg border border-slate-800/80 text-[11px] font-mono space-y-1">
              <div className="flex justify-between text-slate-400">
                <span>Transport Mode:</span>
                <span className="text-white font-bold">TCP Forced (Rule 3)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Reconnection Logic:</span>
                <span className="text-white">Exponential (2s - 30s)</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Timing Source:</span>
                <span className="text-cyan-400">PTS Synchronization</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};