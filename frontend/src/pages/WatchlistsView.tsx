import React, { useState } from 'react';
import { Radio, Plus, ShieldAlert, CheckCircle, Search, Tag, FileText } from 'lucide-react';
import { Watchlist } from '../types';
import { api } from '../services/api';

interface WatchlistsViewProps {
  watchlists: Watchlist[];
  onRefresh: () => void;
}

export const WatchlistsView: React.FC<WatchlistsViewProps> = ({ watchlists, onRefresh }) => {
  const [showModal, setShowModal] = useState(false);
  const [selectedWlId, setSelectedWlId] = useState<string>(watchlists[0]?.id || '');
  const [newPlate, setNewPlate] = useState('');
  const [newReason, setNewReason] = useState('');
  const [newCaseRef, setNewCaseRef] = useState('CASE-2026-X');
  const [newPriority, setNewPriority] = useState('HIGH');

  const handleAddEntry = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPlate || !newReason) return;
    try {
      const targetWl = selectedWlId || watchlists[0]?.id;
      await api.addWatchlistEntry(targetWl, {
        plate_number: newPlate,
        reason: newReason,
        priority: newPriority,
        case_reference: newCaseRef
      });
      setShowModal(false);
      setNewPlate('');
      setNewReason('');
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
            <Radio className="w-5 h-5 text-cyan-400" />
            <h1 className="text-base font-bold text-white tracking-wide">Authorized Watchlist Database</h1>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time automated correlation with active terror, crime, stolen vehicle, and traffic impound hotlists.
          </p>
        </div>

        <button
          onClick={() => {
            if (watchlists.length > 0) setSelectedWlId(watchlists[0].id);
            setShowModal(true);
          }}
          className="flex items-center gap-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg shadow-rose-600/20 transition-all cursor-pointer"
        >
          <Plus className="w-4 h-4" />
          <span>Add Suspect Plate to Watchlist</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {watchlists.map((wl) => (
          <div key={wl.id} className="bg-[#111827] border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div>
                <h2 className="text-sm font-bold text-white tracking-wide">{wl.name}</h2>
                <p className="text-[11px] text-slate-400 mt-0.5">{wl.description}</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-rose-950 text-rose-400 border border-rose-800">
                {wl.priority} PRIORITY
              </span>
            </div>

            <div className="space-y-2.5">
              {wl.entries.map((entry) => (
                <div 
                  key={entry.id}
                  className="bg-[#0b0f19] border border-slate-800 p-3 rounded-lg flex items-center justify-between"
                >
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-white text-xs bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                        {entry.plate_number}
                      </span>
                      <span className="text-[10px] font-mono text-cyan-400">
                        {entry.case_reference}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 font-medium">{entry.reason}</p>
                  </div>

                  <span className="text-[10px] font-mono font-bold text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                    ACTIVE
                  </span>
                </div>
              ))}

              {wl.entries.length === 0 && (
                <div className="text-center py-6 text-xs text-slate-500 font-mono">
                  No suspect plates currently registered in this watchlist.
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-[#111827] border border-slate-800 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center pb-2 border-b border-slate-800">
              <h2 className="text-sm font-bold text-white tracking-wide">Add Suspect Vehicle to Watchlist</h2>
              <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white">&times;</button>
            </div>

            <form onSubmit={handleAddEntry} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1 font-mono">Target Watchlist</label>
                <select 
                  value={selectedWlId} 
                  onChange={(e) => setSelectedWlId(e.target.value)} 
                  className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg p-2 text-white font-mono"
                >
                  {watchlists.map(w => (
                    <option key={w.id} value={w.id}>{w.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">Vehicle Plate Number</label>
                <input 
                  type="text" 
                  required
                  placeholder="e.g. DL-01-AB-1234"
                  value={newPlate} 
                  onChange={(e) => setNewPlate(e.target.value)} 
                  className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg p-2 text-white font-mono font-bold"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1 font-mono">Reason / Flag Detail</label>
                <textarea 
                  required
                  rows={2}
                  placeholder="Reason for flagging..."
                  value={newReason} 
                  onChange={(e) => setNewReason(e.target.value)} 
                  className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg p-2 text-white font-mono"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Priority</label>
                  <select 
                    value={newPriority} 
                    onChange={(e) => setNewPriority(e.target.value)} 
                    className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg p-2 text-white font-mono"
                  >
                    <option value="CRITICAL">CRITICAL</option>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1 font-mono">Case Reference</label>
                  <input 
                    type="text" 
                    value={newCaseRef} 
                    onChange={(e) => setNewCaseRef(e.target.value)} 
                    className="w-full bg-[#0b0f19] border border-slate-700 rounded-lg p-2 text-white font-mono"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 cursor-pointer"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-4 py-2 bg-rose-600 text-white rounded-lg hover:bg-rose-500 font-bold cursor-pointer shadow-lg shadow-rose-600/20"
                >
                  Add to Watchlist
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};