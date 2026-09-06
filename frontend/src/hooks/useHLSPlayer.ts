import { useEffect, useRef } from "react";

export function useHLSPlayer(
  videoRef: React.RefObject<HTMLVideoElement | null>,
  hlsUrl: string | null,
  options?: {
    onError?: () => void;
    onPlaying?: () => void;
  }
) {
  const hlsRef = useRef<any>(null);

  useEffect(() => {
    if (!videoRef.current || !hlsUrl) return;
    const video = videoRef.current;
    let fatalCount = 0;

    const loadHls = async () => {
      try {
        const Hls = (await import("hls.js")).default;
        if (Hls.isSupported()) {
          if (hlsRef.current) hlsRef.current.destroy();
          const hls = new Hls({ lowLatencyMode: true, backBufferLength: 5, maxBufferLength: 10 });
          hlsRef.current = hls;
          hls.loadSource(hlsUrl);
          hls.attachMedia(video);
          hls.on(Hls.Events.MANIFEST_PARSED, () => {
            video.play().then(() => options?.onPlaying?.()).catch(() => {});
          });
          hls.on(Hls.Events.ERROR, (_: any, data: any) => {
            if (data.fatal) {
              fatalCount++;
              if (fatalCount >= 2) {
                options?.onError?.();
              }
              setTimeout(() => {
                if (hlsRef.current) hls.loadSource(hlsUrl);
              }, 3000);
            }
          });
        } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
          video.src = hlsUrl;
          video.play().then(() => options?.onPlaying?.()).catch(() => {});
        }
      } catch (e) {
        console.warn("HLS.js error:", e);
        options?.onError?.();
      }
    };

    loadHls();
    return () => { if (hlsRef.current) { hlsRef.current.destroy(); hlsRef.current = null; } };
  }, [hlsUrl]);
}