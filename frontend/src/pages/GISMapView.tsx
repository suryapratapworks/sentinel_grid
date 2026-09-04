import React, { useEffect, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Map, Layers, Radio, Camera, Compass, Navigation, Zap, AlertTriangle, Eye, Video } from 'lucide-react';
import { Camera as CameraType, VehicleRoute } from '../types';

interface GISMapViewProps {
  cameras: CameraType[];
  highlightRoute?: VehicleRoute | null;
  onSelectCamera?: (cam: CameraType) => void;
}

export const GISMapView: React.FC<GISMapViewProps> = ({ cameras, highlightRoute, onSelectCamera }) => {
  const [selectedCam, setSelectedCam] = useState<CameraType | null>(cameras[0] || null);

  useEffect(() => {
    const mapContainer = document.getElementById('sentinel-leaflet-map');
    if (!mapContainer) return;

    if ((mapContainer as any)._leaflet_map) {
      (mapContainer as any)._leaflet_map.remove();
      (mapContainer as any)._leaflet_map = null;
    }

    const centerLat = cameras.length > 0 ? cameras[0].latitude : 28.6139;
    const centerLon = cameras.length > 0 ? cameras[0].longitude : 77.2090;

    const map = L.map('sentinel-leaflet-map', {
      center: [centerLat, centerLon],
      zoom: 13,
      zoomControl: false
    });
    (mapContainer as any)._leaflet_map = map;

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; Sentinel Grid GIS & CartoDB',
      maxZoom: 19
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Trigger invalidateSize to ensure full map render
    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    cameras.forEach((cam) => {
      const isOnline = cam.status === 'ONLINE';
      const color = isOnline ? '#10b981' : cam.status === 'DEGRADED' ? '#f59e0b' : '#ef4444';
      
      const customIcon = L.divIcon({
        className: 'custom-map-marker',
        html: `<div style="
          width: 18px; 
          height: 18px; 
          border-radius: 50%; 
          background: ${color}; 
          border: 2px solid #ffffff; 
          box-shadow: 0 0 10px ${color};
        "></div>`,
        iconSize: [18, 18],
        iconAnchor: [9, 9]
      });

      const marker = L.marker([cam.latitude, cam.longitude], { icon: customIcon }).addTo(map);
      marker.on('click', () => {
        setSelectedCam(cam);
        if (onSelectCamera) onSelectCamera(cam);
      });

      marker.bindTooltip(`<b>${cam.camera_code}</b>: ${cam.name}`, {
        className: 'bg-slate-900 text-white border border-slate-700 text-xs px-2 py-1 rounded shadow',
        direction: 'top'
      });
    });

    if (highlightRoute && highlightRoute.route.length > 0) {
      const latlngs: L.LatLngTuple[] = highlightRoute.route.map((r) => [r.latitude, r.longitude] as [number, number]);
      const polyline = L.polyline(latlngs, {
        color: '#06b6d4',
        weight: 4,
        opacity: 0.85,
        dashArray: '8, 8'
      }).addTo(map);

      map.fitBounds(polyline.getBounds(), { padding: [50, 50] });

      highlightRoute.route.forEach((node, idx) => {
        const routeIcon = L.divIcon({
          className: 'route-node-marker',
          html: `<div style="
            width: 22px; 
            height: 22px; 
            border-radius: 50%; 
            background: #06b6d4; 
            color: #000;
            font-weight: 800;
            font-size: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid #fff;
            box-shadow: 0 0 12px #06b6d4;
          ">${idx + 1}</div>`,
          iconSize: [22, 22],
          iconAnchor: [11, 11]
        });
        L.marker([node.latitude, node.longitude], { icon: routeIcon }).addTo(map);
      });
    }

    return () => {
      if ((mapContainer as any)._leaflet_map) {
        (mapContainer as any)._leaflet_map.remove();
        (mapContainer as any)._leaflet_map = null;
      }
    };
  }, [cameras, highlightRoute]);

  return (
    <div className="space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-[#111827] p-3.5 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-3">
          <Map className="w-5 h-5 text-cyan-400" />
          <div>
            <h1 className="text-sm font-bold text-white tracking-wide">GIS Tactical Asset Mapping</h1>
            <p className="text-[11px] text-slate-400">Model 1 CCTV Registry Map with Live RTSP Overlay</p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-2 bg-[#0b0f19] px-3 py-1.5 rounded-lg border border-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
            <span className="text-slate-300 font-mono">Online ({cameras.filter(c => c.status === 'ONLINE').length})</span>
          </div>
          <div className="flex items-center gap-2 bg-[#0b0f19] px-3 py-1.5 rounded-lg border border-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-400"></span>
            <span className="text-slate-300 font-mono">Offline ({cameras.filter(c => c.status !== 'ONLINE').length})</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 h-[calc(100vh-14rem)] min-h-[500px]">
        <div className="lg:col-span-3 rounded-xl overflow-hidden border border-slate-800 relative bg-[#0b0f19] shadow-inner">
          <div id="sentinel-leaflet-map" className="w-full h-full" />

          {highlightRoute && (
            <div className="absolute top-4 left-4 z-[400] bg-slate-900/90 border border-cyan-500/50 backdrop-blur px-4 py-2.5 rounded-lg shadow-xl text-xs font-mono">
              <div className="text-cyan-400 font-bold flex items-center gap-2">
                <Navigation className="w-3.5 h-3.5 animate-spin" />
                <span>ACTIVE ROUTE RECONSTRUCTION</span>
              </div>
              <div className="text-slate-200 mt-1">
                Plate: <span className="font-bold text-white">{highlightRoute.plate_number}</span> ({highlightRoute.make_model})
              </div>
              <div className="text-[11px] text-slate-400">
                {highlightRoute.total_points} Camera Sightings • {highlightRoute.total_distance_km} km Corridor
              </div>
            </div>
          )}
        </div>

        <div className="bg-[#111827] border border-slate-800 rounded-xl p-4 flex flex-col justify-between overflow-y-auto space-y-4">
          {selectedCam ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-800 text-cyan-400 border border-slate-700">
                    {selectedCam.camera_code}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    selectedCam.status === 'ONLINE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'
                  }`}>
                    {selectedCam.status}
                  </span>
                </div>
                <h2 className="text-sm font-bold text-white mt-2 leading-snug">{selectedCam.name}</h2>
                <p className="text-[11px] text-slate-400 font-mono mt-0.5">{selectedCam.department_name}</p>
              </div>

              <div className="relative aspect-video bg-black rounded-lg overflow-hidden border border-slate-800 flex items-center justify-center group">
                {(() => {
                  const rawUrl = selectedCam.streams && selectedCam.streams.length > 0 ? (selectedCam.streams[0] as any).stream_url_encrypted || '' : '';
                  const match = rawUrl.match(/https?:\/\/([^/]+)/) || rawUrl.match(/rtsp:\/\/([^/]+)/);
                  const feedUrl = match ? `http://${match[1]}/video` : null;
                  return feedUrl ? (
                    <img
                      src={feedUrl}
                      alt={selectedCam.name}
                      className="absolute inset-0 w-full h-full object-cover z-10"
                      onError={(e) => {
                        (e.target as any).style.display = 'none';
                      }}
                    />
                  ) : null;
                })()}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/40 z-20 pointer-events-none" />

                <div className="absolute top-2 left-2 z-30 flex items-center gap-1.5 bg-black/70 px-2 py-0.5 rounded text-[10px] font-mono text-cyan-400 font-bold border border-cyan-500/30">
                  <Radio className="w-3 h-3 text-cyan-400 animate-pulse" />
                  <span>LIVE RTSP / TCP</span>
                </div>

                <div className="absolute bottom-2 left-2 right-2 z-30 flex justify-between text-[10px] font-mono text-slate-300">
                  <span>{selectedCam.codec} • {selectedCam.resolution}</span>
                  <span className="text-emerald-400 font-bold">{selectedCam.fps} FPS</span>
                </div>
              </div>

              <div className="space-y-2 text-xs font-mono bg-[#0b0f19] p-3 rounded-lg border border-slate-800/80">
                <div className="flex justify-between text-slate-400">
                  <span>Vendor:</span>
                  <span className="text-white">{selectedCam.vendor}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Model:</span>
                  <span className="text-white">{selectedCam.model}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Protocol:</span>
                  <span className="text-cyan-400">{selectedCam.protocol}</span>
                </div>
                <div className="flex justify-between text-slate-400">
                  <span>Lat / Lon:</span>
                  <span className="text-slate-300">{selectedCam.latitude.toFixed(4)}, {selectedCam.longitude.toFixed(4)}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-xs text-slate-500 font-mono">
              Select a camera pin on the GIS map to inspect live feeds and telemetry.
            </div>
          )}

          <div className="text-[10px] text-slate-500 font-mono text-center">
            PTS-Synchronized GIS Feed Matrix
          </div>
        </div>
      </div>
    </div>
  );
};