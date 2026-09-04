import React, { useState, useEffect } from 'react';
import { 
  Camera as CameraIcon, Plus, 
  Search, ArrowDownToLine, Radio, Shield, Video, Smartphone,
  Trash2, AlertTriangle
} from 'lucide-react';
import { Camera, AuthUser } from '../types';
import { api } from '../services/api';

interface CameraRegistryViewProps {
  cameras: Camera[];
  currentUser?: AuthUser | null;
  onRefresh: () => void;
  onSelectCamera: (cam: Camera) => void;
}

export const CameraRegistryView: React.FC<CameraRegistryViewProps> = ({ cameras, currentUser, onRefresh, onSelectCamera }) => {
  const [departments, setDepartments] = useState<{ id: string; name: string; code: string }[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [protocolFilter, setProtocolFilter] = useState('ALL');
  const [syncingCatalogue, setSyncingCatalogue] = useState(false);
  const [syncFeedback, setSyncFeedback] = useState<string | null>(null);
  const [deletingCamId, setDeletingCamId] = useState<string | null>(null);

  const isSuperAdmin = currentUser?.role === 'SUPER_ADMIN';

  const [showAddModal, setShowAddModal] = useState(false);
  const [newCamCode, setNewCamCode] = useState('');
  const [newCamName, setNewCamName] = useState('');
  const [newCamDeptId, setNewCamDeptId] = useState('');
  const [newCamVendor, setNewCamVendor] = useState('Android / iOS Phone Camera');
  const [newCamProtocol, setNewCamProtocol] = useState('RTSP');
  const [newCamCodec, setNewCamCodec] = useState('H.264');
  const [newCamStreamUrl, setNewCamStreamUrl] = useState('');
  const [newCamLat, setNewCamLat] = useState('28.6139');
  const [newCamLon, setNewCamLon] = useState('77.2090');

  useEffect(() => {
    api.getDepartments().then(depts => {
      setDepartments(depts);
      if (depts.length > 0 && !newCamDeptId) {
        setNewCamDeptId(depts[0].id);
      }
    }).catch(() => {});
  }, []);

  const filteredCameras = cameras.filter((cam) => {
    const matchesSearch = cam.camera_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          cam.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          cam.vendor.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || cam.status === statusFilter;
    const matchesProtocol = protocolFilter === 'ALL' || cam.protocol === protocolFilter;
    return matchesSearch && matchesStatus && matchesProtocol;
  });

  const handleCatalogueSync = async () => {
    setSyncingCatalogue(true);
    setSyncFeedback(null);
    try {
      const res = await api.ingestCatalogue();
      setSyncFeedback(`Discovery scan complete: ${res.total_discovered} active devices verified.`);
      onRefresh();
    } catch (e: any) {
      setSyncFeedback(`Discovery scan error: ${e.message}`);
    } finally {
      setSyncingCatalogue(false);
    }
  };

  const handleDeleteCamera = async (cam: Camera) => {
    if (!isSuperAdmin) {
      alert('Unauthorized: Only Super Administrators can delete cameras from the registry.');
      return;
    }

    const confirmDelete = window.confirm(
      `⚠️ PERMANENT CAMERA REMOVAL\n\nAre you sure you want to permanently delete this camera?\n\nCode: ${cam.camera_code}\nName: ${cam.name}\nDepartment: ${cam.department_name || 'General'}\n\nThis action cannot be undone.`
    );

    if (!confirmDelete) return;

    try {
      setDeletingCamId(cam.id);
      const res = await api.deleteCamera(cam.id);
      setSyncFeedback(res.message || `Camera ${cam.camera_code} deleted successfully.`);
      onRefresh();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    } finally {
      setDeletingCamId(null);
    }
  };

  const handleCreateCamera = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCamCode || !newCamName) return;
    try {
      const deptId = newCamDeptId || (departments.length > 0 ? departments[0].id : '');
      if (!deptId) {
        alert('Please select an authoritative department.');
        return;
      }

      await api.createCamera({
        camera_code: newCamCode,
        name: newCamName,
        department_id: deptId,
        vendor: newCamVendor,
        protocol: newCamProtocol,
        codec: newCamCodec,
        stream_url: newCamStreamUrl || undefined,
        latitude: parseFloat(newCamLat) || 28.6139,
        longitude: parseFloat(newCamLon) || 77.2090,
        integration_type: newCamProtocol === 'ONVIF' ? 'ONVIF' : 'DIRECT_RTSP'
      });

      setShowAddModal(false);
      setNewCamCode('');
      setNewCamName('');
      setNewCamStreamUrl('');
      onRefresh();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="space-y-4 pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-surface p-4 rounded-xl border border-border">
        <div>
          <div className="flex items-center space-x-2">
            <CameraIcon className="w-5 h-5 text-cyan-400" />
            <h1 className="text-base font-bold text-primary tracking-wide">Model 1 — Central CCTV Registry</h1>
          </div>
          <p className="text-xs text-muted mt-0.5">
            Unified statewide inventory mapping heterogeneous camera vendors, RTSP streams, ONVIF discovery, and telemetry.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleCatalogueSync}
            disabled={syncingCatalogue}
            className="flex items-center gap-2 bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/50 text-xs font-bold px-3.5 py-2 rounded-lg transition-all cursor-pointer disabled:opacity-50"
            title="Scan network for ONVIF & dynamic streams"
          >
            <ArrowDownToLine className={`w-4 h-4 ${syncingCatalogue ? 'animate-bounce' : ''}`} />
            <span>{syncingCatalogue ? 'Scanning Network...' : 'Scan Subnet / Catalogue'}</span>
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-3.5 py-2 rounded-lg shadow transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            <span>Onboard Camera</span>
          </button>
        </div>
      </div>

      {syncFeedback && (
        <div className="bg-surface border border-cyan-500/40 p-3 rounded-lg text-xs font-mono flex items-center justify-between text-cyan-400">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span>{syncFeedback}</span>
          </div>
          <button onClick={() => setSyncFeedback(null)} className="text-muted hover:text-primary">&times;</button>
        </div>
      )}

      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-3 bg-surface p-3 rounded-xl border border-border">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-muted absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search cameras by code, name, vendor..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-base border border-border rounded-lg pl-9 pr-4 py-1.5 text-xs text-primary placeholder-muted focus:outline-none focus:border-cyan-500 font-mono"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-base border border-border rounded-lg px-3 py-1.5 text-xs text-primary font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="ONLINE">ONLINE</option>
            <option value="OFFLINE">OFFLINE</option>
            <option value="DEGRADED">DEGRADED</option>
          </select>

          <select
            value={protocolFilter}
            onChange={(e) => setProtocolFilter(e.target.value)}
            className="bg-base border border-border rounded-lg px-3 py-1.5 text-xs text-primary font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Protocols</option>
            <option value="RTSP">RTSP / TCP</option>
            <option value="ONVIF">ONVIF</option>
            <option value="VMS_ADAPTER">VMS Bridge</option>
          </select>
        </div>
      </div>

      {/* Camera Table or Empty State */}
      {filteredCameras.length === 0 ? (
        <div className="bg-surface border border-border rounded-xl p-12 text-center space-y-4 shadow-xl">
          <div className="w-16 h-16 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400">
            <Video className="w-8 h-8" />
          </div>
          <div>
            <h3 className="text-base font-bold text-primary">No Cameras Ingested Yet</h3>
            <p className="text-xs text-muted max-w-md mx-auto mt-1 font-mono">
              The camera registry is ready for real operational devices. Onboard your mobile phone camera or physical RTSP/ONVIF IP cameras.
            </p>
          </div>
          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={() => {
                setNewCamCode('CAM-PHONE-001');
                setNewCamName('Mobile Patrol Unit 1');
                setNewCamVendor('Mobile IP Camera');
                setNewCamProtocol('RTSP');
                setNewCamStreamUrl('rtsp://192.168.1.100:8080/h264_ulaw.sdp');
                setShowAddModal(true);
              }}
              className="flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold px-4 py-2 rounded-lg shadow-lg shadow-cyan-500/20 transition-all cursor-pointer font-mono"
            >
              <Smartphone className="w-4 h-4" />
              <span>Onboard Phone Camera</span>
            </button>
            <button
              onClick={() => setShowAddModal(true)}
              className="flex items-center gap-2 border border-border hover:border-cyan-500 text-muted hover:text-primary text-xs font-bold px-4 py-2 rounded-lg transition-all cursor-pointer font-mono"
            >
              <Plus className="w-4 h-4" />
              <span>Onboard IP Camera</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-surface border border-border rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-primary">
              <thead className="bg-base text-[10px] uppercase font-mono font-bold text-muted border-b border-border tracking-wider">
                <tr>
                  <th className="p-3.5">Code</th>
                  <th className="p-3.5">Camera Name</th>
                  <th className="p-3.5">Department</th>
                  <th className="p-3.5">Vendor / Model</th>
                  <th className="p-3.5">Protocol</th>
                  <th className="p-3.5">Resolution / FPS</th>
                  <th className="p-3.5">Coordinates</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-mono">
                {filteredCameras.map((cam) => (
                  <tr key={cam.id} className="hover:bg-elevated transition-colors">
                    <td className="p-3.5 font-bold text-cyan-400">{cam.camera_code}</td>
                    <td className="p-3.5 font-semibold text-primary">{cam.name}</td>
                    <td className="p-3.5 text-muted">{cam.department_name || 'General'}</td>
                    <td className="p-3.5 text-muted">{cam.vendor} {cam.model ? `(${cam.model})` : ''}</td>
                    <td className="p-3.5">
                      <span className="bg-base text-primary px-2 py-0.5 rounded text-[10px] border border-border">
                        {cam.protocol}
                      </span>
                    </td>
                    <td className="p-3.5 text-muted">{cam.resolution} @ {cam.fps}fps</td>
                    <td className="p-3.5 text-muted text-[11px]">{cam.latitude.toFixed(4)}, {cam.longitude.toFixed(4)}</td>
                    <td className="p-3.5">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold ${
                        cam.status === 'ONLINE'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                          : 'bg-rose-500/10 text-rose-400 border border-rose-500/30'
                      }`}>
                        {cam.status}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => onSelectCamera(cam)}
                          className="text-cyan-400 hover:text-cyan-300 font-bold underline cursor-pointer text-xs"
                        >
                          Locate on GIS
                        </button>
                        {isSuperAdmin && (
                          <button
                            onClick={() => handleDeleteCamera(cam)}
                            disabled={deletingCamId === cam.id}
                            title="Delete Camera (Super Admin Privilege)"
                            className="inline-flex items-center gap-1 bg-rose-500/10 hover:bg-rose-500/25 text-rose-400 hover:text-rose-300 border border-rose-500/30 px-2 py-1 rounded text-[11px] font-bold transition-all cursor-pointer disabled:opacity-50"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                            <span>{deletingCamId === cam.id ? 'Deleting...' : 'Delete'}</span>
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Onboard Camera Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-surface border border-border rounded-xl w-full max-w-lg p-6 space-y-4 shadow-2xl">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <h3 className="text-base font-bold text-primary flex items-center gap-2">
                <CameraIcon className="w-5 h-5 text-cyan-400" />
                <span>Onboard Live Camera to Registry</span>
              </h3>
              <button onClick={() => setShowAddModal(false)} className="text-muted hover:text-primary">&times;</button>
            </div>

            <form onSubmit={handleCreateCamera} className="space-y-3 font-mono text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-muted mb-1 text-[11px]">Camera Code</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. CAM-PHONE-001"
                    value={newCamCode}
                    onChange={(e) => setNewCamCode(e.target.value)}
                    className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-muted mb-1 text-[11px]">Department</label>
                  <select
                    value={newCamDeptId}
                    onChange={(e) => setNewCamDeptId(e.target.value)}
                    className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                  >
                    {departments.map(d => (
                      <option key={d.id} value={d.id}>{d.name} ({d.code})</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-muted mb-1 text-[11px]">Camera Name / Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Mobile Patrol Phone Stream 1"
                  value={newCamName}
                  onChange={(e) => setNewCamName(e.target.value)}
                  className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-muted mb-1 text-[11px]">Protocol</label>
                  <select
                    value={newCamProtocol}
                    onChange={(e) => setNewCamProtocol(e.target.value)}
                    className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                  >
                    <option value="RTSP">RTSP (Forced TCP)</option>
                    <option value="ONVIF">ONVIF</option>
                    <option value="VMS_ADAPTER">VMS Bridge</option>
                  </select>
                </div>
                <div>
                  <label className="block text-muted mb-1 text-[11px]">Vendor / Hardware</label>
                  <input
                    type="text"
                    placeholder="e.g. Android IP Webcam, Axis, Hikvision"
                    value={newCamVendor}
                    onChange={(e) => setNewCamVendor(e.target.value)}
                    className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-muted mb-1 text-[11px]">Live Stream URL (RTSP / Phone)</label>
                <input
                  type="text"
                  placeholder="rtsp://192.168.1.100:8080/h264_ulaw.sdp"
                  value={newCamStreamUrl}
                  onChange={(e) => setNewCamStreamUrl(e.target.value)}
                  className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-muted mb-1 text-[11px]">Latitude</label>
                  <input
                    type="number"
                    step="any"
                    value={newCamLat}
                    onChange={(e) => setNewCamLat(e.target.value)}
                    className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-muted mb-1 text-[11px]">Longitude</label>
                  <input
                    type="number"
                    step="any"
                    value={newCamLon}
                    onChange={(e) => setNewCamLon(e.target.value)}
                    className="w-full bg-base border border-border rounded-lg p-2 text-primary focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-border rounded-lg text-muted hover:text-primary text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg font-bold text-xs shadow cursor-pointer"
                >
                  Register Camera
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};