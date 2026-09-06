import React, { useState, useRef, useEffect } from 'react';
import { Video, Wifi, WifiOff, Maximize2, RefreshCw, Radio, Smartphone, AlertCircle, RotateCw } from 'lucide-react';
import { Camera } from '../types';
import { useHLSPlayer } from '../hooks/useHLSPlayer';

interface LiveMatrixViewProps {
  cameras: Camera[];
  onRefresh: () => void;
}

type Layout = '1x1' | '2x2' | '3x3';

const HLSVideoCell: React.FC<{ camera: Camera; isActive: boolean }> = ({ camera, isActive }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const slug = camera.camera_code.toLowerCase().replace(/-/g, '_');
  const hlsUrl = isActive ? `http://localhost:8888/${slug}/index.m3u8` : null;

  const [streamError, setStreamError] = useState(false);
  const [streamLoaded, setStreamLoaded] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  // Extract raw stream URL and host
  const rawStreamUrl = (camera.streams && camera.streams.length > 0 && camera.streams[0].stream_url) 
    ? camera.streams[0].stream_url 
    : '';

  const ipMatch = rawStreamUrl.match(/(?:https?|rtsp):\/\/([^/]+)/);
  const targetHost = ipMatch ? ipMatch[1] : '';

  // Determine if camera is a phone or IP Webcam
  const isPhoneOrHttp = camera.protocol === 'HTTP' || 
                        camera.vendor.toLowerCase().includes('phone') || 
                        camera.vendor.toLowerCase().includes('mobile') || 
                        camera.vendor.toLowerCase().includes('webcam') ||
                        rawStreamUrl.includes('8080');

  // Stream mode: 'proxy' (backend live MJPEG) or 'hls' (MediaMTX)
  const [useProxy, setUseProxy] = useState(isPhoneOrHttp);

  useHLSPlayer(videoRef, (!useProxy && isActive) ? hlsUrl : null, {
    onError: () => {
      // HLS failed, auto fallback to backend live MJPEG proxy
      setUseProxy(true);
    },
    onPlaying: () => {
      setStreamLoaded(true);
      setStreamError(false);
    }
  });

  const handleRetry = () => {
    setStreamError(false);
    setStreamLoaded(false);
    setRetryCount(prev => prev + 1);
  };

  const proxyUrl = `/api/cameras/${camera.id}/live?k=${retryCount}`;

  return (
    <div className="relative w-full h-full bg-[#080c14] rounded overflow-hidden group">
      {isActive && !streamError ? (
        useProxy ? (
          <img
            key={`stream-${camera.id}-${retryCount}`}
            src={proxyUrl}
            alt={camera.name}
            className="w-full h-full object-cover"
            onLoad={() => {
              setStreamLoaded(true);
              setStreamError(false);
            }}
            onError={() => {
              setStreamError(true);
              setStreamLoaded(false);
            }}
          />
        ) : (
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            muted
            playsInline
            autoPlay
            onError={() => {
              setUseProxy(true);
            }}
          />
        )
      ) : null}

      {/* Offline or Error Diagnostic Card */}
      {(streamError || !isActive) && (
        <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-[#0b0f19] text-center">
          <div className="w-10 h-10 rounded-full bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mb-2">
            {isPhoneOrHttp ? (
              <Smartphone className="w-5 h-5 text-rose-400" />
            ) : (
              <AlertCircle className="w-5 h-5 text-rose-400" />
            )}
          </div>
          <p className="text-xs font-bold text-slate-200">
            {isPhoneOrHttp ? 'Phone Camera Offline / Unreachable' : 'Stream Feed Offline'}
          </p>
          {targetHost && (
            <p className="text-[11px] font-mono text-cyan-400 mt-0.5">
              {targetHost}
            </p>
          )}

          {isPhoneOrHttp && (
            <div className="mt-2 text-[10px] text-slate-400 font-mono space-y-0.5 max-w-[220px]">
              <p>1. Open IP Webcam app on phone</p>
              <p>2. Tap "Start server" at bottom</p>
              <p>3. Keep screen unlocked on same Wi-Fi</p>
            </div>
          )}

          <button
            onClick={handleRetry}
            className="mt-3 inline-flex items-center gap-1.5 bg-cyan-600/20 hover:bg-cyan-600/30 text-cyan-400 border border-cyan-500/40 px-3 py-1 rounded text-xs font-bold transition-all cursor-pointer"
          >
            <RotateCw className="w-3 h-3" />
            <span>Reconnect Stream</span>
          </button>
        </div>
      )}

      {/* Live HUD Overlay */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top bar */}
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-black/80 via-black/40 to-transparent p-2 flex justify-between items-start pointer-events-auto">
          <div>
            <div className="text-white text-xs font-bold font-mono flex items-center gap-1.5">
              <span>{camera.camera_code}</span>
              {isPhoneOrHttp && (
                <span className="bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-[9px] px-1 py-0.2 rounded font-sans">
                  PHONE
                </span>
              )}
            </div>
            <div className="text-slate-400 text-[10px] font-mono">{camera.name}</div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => {
                setUseProxy(!useProxy);
                handleRetry();
              }}
              title={`Switch stream engine (currently: ${useProxy ? 'MJPEG Live' : 'HLS Relay'})`}
              className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all cursor-pointer"
            >
              {useProxy ? 'LIVE' : 'HLS'}
            </button>
            <div className={`flex items-center gap-1 text-[10px] font-bold px-1.5 py-0.5 rounded ${
              isActive && !streamError ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
            }`}>
              {isActive && !streamError ? <Wifi className="w-2.5 h-2.5" /> : <WifiOff className="w-2.5 h-2.5" />}
              {isActive && !streamError ? 'ONLINE' : 'OFFLINE'}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-2 flex justify-between items-end">
          <span className="text-[10px] font-mono text-slate-400">
            {camera.protocol} | {camera.codec}
          </span>
          <div className="flex items-center gap-1">
            {isActive && !streamError && (
              <span className="flex items-center gap-0.5 text-[10px] text-red-400 font-bold">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
                LIVE
              </span>
            )}
            <span className="text-[10px] font-mono text-slate-400">{camera.fps}fps</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export const LiveMatrixView: React.FC<LiveMatrixViewProps> = ({ cameras, onRefresh }) => {
  const [layout, setLayout] = useState<Layout>('2x2');
  const [activePage, setActivePage] = useState(0);

  const gridConfig = {
    '1x1': { cols: 1, count: 1 },
    '2x2': { cols: 2, count: 4 },
    '3x3': { cols: 3, count: 9 },
  };

  const { cols, count } = gridConfig[layout];
  const visibleCameras = cameras.slice(activePage * count, (activePage + 1) * count);
  const totalPages = Math.ceil(cameras.length / count);

  const filledCameras = [
    ...visibleCameras,
    ...Array(Math.max(0, count - visibleCameras.length)).fill(null)
  ];

  return (
    <div className="flex flex-col h-full space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-black text-primary tracking-wide uppercase">Video Wall Matrix</h2>
          <p className="text-xs text-muted font-mono">
            HLS streams via MediaMTX (localhost:8888) &bull; {cameras.filter(c => c.status === 'ONLINE').length} feeds live
          </p>
        </div>
        <div className="flex items-center gap-2">
          {(['1x1', '2x2', '3x3'] as Layout[]).map(l => (
            <button
              key={l}
              onClick={() => { setLayout(l); setActivePage(0); }}
              className={`px-3 py-1.5 text-xs font-bold rounded border transition-all cursor-pointer ${
                layout === l
                  ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-400'
                  : 'border-border text-muted hover:border-slate-600'
              }`}
            >
              {l}
            </button>
          ))}
          <button onClick={onRefresh} className="p-2 rounded border border-border text-muted hover:text-cyan-400 transition-all cursor-pointer">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* MediaMTX status bar */}
      <div className="flex items-center gap-2 px-3 py-2 bg-surface rounded-lg border border-border text-xs font-mono">
        <Radio className="w-3.5 h-3.5 text-cyan-400" />
        <span className="text-muted">MediaMTX Relay:</span>
        <span className="text-cyan-400">HLS :8888</span>
        <span className="text-border">|</span>
        <span className="text-emerald-400">WebRTC :8889</span>
        <span className="text-border">|</span>
        <span className="text-amber-400">RTSP :8554</span>
        <span className="ml-auto text-muted">
          Start: <span className="text-primary">python start.py --phone-ip YOUR_PHONE_IP</span>
        </span>
      </div>

      {/* Video Grid */}
      <div
        className="flex-1 grid gap-2"
        style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
      >
        {filledCameras.map((cam, idx) => (
          <div key={cam ? cam.id : `empty-${idx}`} className="bg-[#0b0f19] rounded-lg border border-border overflow-hidden min-h-0" style={{ minHeight: '140px' }}>
            {cam ? (
              <HLSVideoCell camera={cam} isActive={cam.status === 'ONLINE'} />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-slate-700">
                <Video className="w-8 h-8 opacity-20" />
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          {Array.from({ length: totalPages }, (_, i) => (
            <button
              key={i}
              onClick={() => setActivePage(i)}
              className={`w-7 h-7 text-xs font-bold rounded border transition-all cursor-pointer ${
                activePage === i
                  ? 'bg-cyan-500/20 border-cyan-500 text-cyan-400'
                  : 'border-border text-muted hover:border-slate-600'
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};