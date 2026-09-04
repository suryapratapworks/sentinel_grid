import React, { useState, useEffect } from 'react';
import { Search, Car, Navigation, Clock, MapPin, ShieldAlert, Zap, AlertCircle } from 'lucide-react';
import { Vehicle, VehicleRoute } from '../types';
import { api } from '../services/api';

interface VehicleInvestigatorViewProps {
  onShowOnMap: (route: VehicleRoute) => void;
}

export const VehicleInvestigatorView: React.FC<VehicleInvestigatorViewProps> = ({ onShowOnMap }) => {
  const [queryPlate, setQueryPlate] = useState('');
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [activeRoute, setActiveRoute] = useState<VehicleRoute | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (plateToSearch?: string) => {
    const term = plateToSearch !== undefined ? plateToSearch : queryPlate;
    setLoading(true);
    try {
      const results = await api.searchVehicles(term);
      setVehicles(results);
      if (results.length > 0) {
        setSelectedVehicle(results[0]);
        try {
          const routeData = await api.getVehicleRoute(results[0].normalized_plate);
          setActiveRoute(routeData);
        } catch (e) {
          setActiveRoute(null);
        }
      } else {
        setSelectedVehicle(null);
        setActiveRoute(null);
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSearch('');
  }, []);

  return (
    <div className="space-y-4 pb-12">
      <div className="bg-surface p-5 rounded-xl border border-border space-y-4 shadow-xl">
        <div className="flex items-center space-x-2">
          <Search className="w-5 h-5 text-cyan-400" />
          <div>
            <h1 className="text-base font-bold text-primary tracking-wide">Vehicle Movement & Route Reconstruction</h1>
            <p className="text-xs text-muted">
              Chronological Presentation Timestamp (PTS) cross-camera correlation and automatic GIS trajectory reconstruction.
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Car className="w-4 h-4 absolute left-3.5 top-3 text-cyan-400" />
            <input
              type="text"
              placeholder="Enter Vehicle Registration Plate (e.g. DL-01-AB-1234)..."
              value={queryPlate}
              onChange={(e) => setQueryPlate(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full bg-base border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-primary font-mono font-bold focus:outline-none focus:border-cyan-500"
            />
          </div>

          <button
            onClick={() => handleSearch()}
            disabled={loading}
            className="w-full md:w-auto bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs px-6 py-2.5 rounded-lg shadow-lg shadow-cyan-500/20 transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Search className="w-4 h-4" />
            <span>{loading ? 'Reconstructing...' : 'Investigate Vehicle'}</span>
          </button>
        </div>

        {vehicles.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <span className="text-muted">Detected Targets:</span>
            {vehicles.slice(0, 8).map((v) => (
              <button
                key={v.id}
                onClick={() => {
                  setQueryPlate(v.plate_number);
                  setSelectedVehicle(v);
                  api.getVehicleRoute(v.normalized_plate).then(setActiveRoute).catch(() => setActiveRoute(null));
                }}
                className={`px-2.5 py-1 rounded border transition-all cursor-pointer ${
                  selectedVehicle?.id === v.id
                    ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400 font-bold'
                    : 'bg-base border-border text-muted hover:border-slate-600'
                }`}
              >
                {v.plate_number} ({v.total_sightings} hits)
              </button>
            ))}
          </div>
        )}
      </div>

      {selectedVehicle ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Target Profile Card */}
          <div className="bg-surface border border-border rounded-xl p-5 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <span className="text-xs font-bold text-muted font-mono uppercase">Target Profile</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                PTS Verified
              </span>
            </div>

            <div className="space-y-3 font-mono text-xs">
              <div className="bg-base p-3 rounded-lg border border-border text-center">
                <div className="text-[10px] text-muted uppercase">Normalized License Plate</div>
                <div className="text-xl font-black text-cyan-400 tracking-wider mt-0.5">
                  {selectedVehicle.plate_number}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-[11px]">
                <div className="bg-base p-2 rounded border border-border">
                  <div className="text-muted text-[10px]">Vehicle Type</div>
                  <div className="font-bold text-primary">{selectedVehicle.vehicle_type || 'Unknown'}</div>
                </div>
                <div className="bg-base p-2 rounded border border-border">
                  <div className="text-muted text-[10px]">Make / Model</div>
                  <div className="font-bold text-primary">{selectedVehicle.make_model || 'Unknown'}</div>
                </div>
              </div>

              <div className="space-y-1.5 pt-2 border-t border-border text-[11px]">
                <div className="flex justify-between text-muted">
                  <span>First Sighted:</span>
                  <span className="text-primary font-bold">{new Date(selectedVehicle.first_seen_at).toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>Last Sighted:</span>
                  <span className="text-primary font-bold">{new Date(selectedVehicle.last_seen_at).toLocaleTimeString()}</span>
                </div>
                <div className="flex justify-between text-muted">
                  <span>Total Correlated Hits:</span>
                  <span className="text-cyan-400 font-bold">{selectedVehicle.total_sightings} sightings</span>
                </div>
              </div>

              {activeRoute && (
                <button
                  onClick={() => onShowOnMap(activeRoute)}
                  className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all cursor-pointer flex items-center justify-center gap-2 mt-2"
                >
                  <Navigation className="w-4 h-4" />
                  <span>Display Reconstructed Route on GIS Map</span>
                </button>
              )}
            </div>
          </div>

          {/* Chronological Milestone Timeline */}
          <div className="lg:col-span-2 bg-surface border border-border rounded-xl p-5 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-xs font-bold text-primary font-mono uppercase">
                  Chronological Movement Trajectory (PTS Strict Ordering)
                </h3>
                <p className="text-[11px] text-muted mt-0.5">
                  Reconstructed cross-camera timeline based on stream Presentation Timestamps.
                </p>
              </div>
              {activeRoute && (
                <span className="text-xs font-bold font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-1 rounded">
                  {activeRoute.total_distance_km.toFixed(2)} km Total Distance
                </span>
              )}
            </div>

            <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-3 before:bottom-3 before:w-0.5 before:bg-border">
              {activeRoute && activeRoute.route.length > 0 ? (
                activeRoute.route.map((node, index) => (
                  <div key={index} className="relative group">
                    <div className="absolute -left-6 top-1 w-4 h-4 rounded-full bg-cyan-500 border-2 border-surface shadow flex items-center justify-center text-[8px] font-bold text-black">
                      {node.sequence}
                    </div>
                    <div className="bg-base p-3 rounded-lg border border-border hover:border-cyan-500/40 transition-colors font-mono text-xs">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-1">
                        <span className="font-bold text-primary text-xs">{node.camera_code} — {node.camera_name}</span>
                        <span className="text-[10px] text-cyan-400">{new Date(node.timestamp).toLocaleTimeString()} (PTS: {node.pts_ms})</span>
                      </div>
                      <div className="mt-2 flex items-center gap-4 text-[10px] text-muted">
                        <span>Speed: <strong className="text-primary">{node.speed_kmh} km/h</strong></span>
                        <span>Confidence: <strong className="text-emerald-400">{(node.confidence * 100).toFixed(1)}%</strong></span>
                        <span>GPS: <strong className="text-muted">{node.latitude.toFixed(4)}, {node.longitude.toFixed(4)}</strong></span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted font-mono text-xs">
                  No multi-camera route points recorded for this target yet.
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl p-12 text-center space-y-3 shadow-xl">
          <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
            <Car className="w-6 h-6" />
          </div>
          <h3 className="text-sm font-bold text-primary">Ready for Vehicle Investigation</h3>
          <p className="text-xs text-muted max-w-md mx-auto font-mono">
            Enter any target registration plate above to reconstruct chronological movement across the camera grid with speed and trip distance telemetry.
          </p>
        </div>
      )}
    </div>
  );
};