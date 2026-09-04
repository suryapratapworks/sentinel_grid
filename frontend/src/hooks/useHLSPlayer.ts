import { useEffect, useRef } from "react";

export function useHLSPlayer(
  videoRef: React.RefObject<HTMLVideoElement | null>,
  hlsUrl: string | null
) {
  const hlsRef = useRef<any>(null);

  useEffect(() => {
    if (!videoRef.current || !hlsUrl) return;
    const video = videoRef.current;

    const loadHls = async () => {
      try {
        const Hls = (await import("hls.js")).default;
        if (Hls.isSupported()) {
          if (hlsRef.current) hlsRef.current.destroy();
          const hls = new Hls({ lowLatencyMode: true, backBufferLength: 5, maxBufferLength: 10 });
          hlsRef.current = hls;
          hls.loadSource(hlsUrl);
          hls.attachMedia(video);
          hls.on(Hls.Events.MANIFEST_PARSED, () => { video.play().catch(() => {}); });
          hls.on(Hls.Events.ERROR, (_: any, data: any) => {
            if (data.fatal) setTimeout(() => hls.loadSource(hlsUrl), 3000);
          });
        } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
          video.src = hlsUrl;
          video.play().catch(() => {});
        }
      } catch (e) { console.warn("HLS.js error:", e); }
    };

    loadHls();
    return () => { if (hlsRef.current) { hlsRef.current.destroy(); hlsRef.current = null; } };
  }, [hlsUrl]);
}