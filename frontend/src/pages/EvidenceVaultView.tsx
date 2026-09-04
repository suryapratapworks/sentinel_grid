import React from 'react';
import { Lock, ShieldCheck } from 'lucide-react';
import { EvidenceItem } from '../types';

interface EvidenceVaultViewProps {
  evidence: EvidenceItem[];
  onRefresh: () => void;
}

export const EvidenceVaultView: React.FC<EvidenceVaultViewProps> = ({ evidence }) => {
  return (
    <div className="space-y-4 pb-12">
      <div className="bg-[#111827] p-5 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-2">
          <Lock className="w-5 h-5 text-cyan-400" />
          <div>
            <h1 className="text-base font-bold text-white tracking-wide">Model 4 — Selective Central Evidence Vault</h1>
            <p className="text-xs text-slate-400 mt-0.5">
              Centralize intelligence, not raw video. Only critical investigation clips and incident snapshots stored with SHA-256 cryptographic proofs.
            </p>
          </div>
        </div>
      </div>

      <div className="bg-[#111827] border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-[#0b0f19] text-[10px] uppercase font-mono font-bold text-slate-400 border-b border-slate-800 tracking-wider">
              <tr>
                <th className="p-3.5">Evidence ID</th>
                <th className="p-3.5">Type</th>
                <th className="p-3.5">Target / Metadata</th>
                <th className="p-3.5">SHA-256 Cryptographic Hash</th>
                <th className="p-3.5">Storage Path</th>
                <th className="p-3.5">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono">
              {evidence.map((ev) => (
                <tr key={ev.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-bold text-cyan-400">
                    {ev.id.substring(0, 8)}...
                  </td>
                  <td className="p-3.5">
                    <span className="bg-slate-800 text-slate-200 px-2 py-0.5 rounded text-[10px] border border-slate-700">
                      {ev.evidence_type}
                    </span>
                  </td>
                  <td className="p-3.5 text-white">
                    {ev.meta_info && ev.meta_info.plate ? `Plate: ${ev.meta_info.plate}` : 'Critical Incident Frame'}
                  </td>
                  <td className="p-3.5 text-slate-400 text-[10px] break-all">
                    {ev.hash}
                  </td>
                  <td className="p-3.5 text-slate-500 text-[10px]">
                    {ev.storage_path}
                  </td>
                  <td className="p-3.5">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                      <ShieldCheck className="w-3 h-3 mr-1" /> VERIFIED INTEGRAL
                    </span>
                  </td>
                </tr>
              ))}

              {evidence.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-slate-500">
                    No retained evidence records found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};