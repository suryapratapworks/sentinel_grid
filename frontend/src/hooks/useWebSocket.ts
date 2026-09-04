import { useEffect, useRef, useCallback, useState } from "react";

export interface WSMessage { type: "alert" | "anpr" | "ping"; data?: any; }

export function useWebSocket(onMessage: (msg: WSMessage) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    const wsUrl = `ws://${window.location.hostname}:8000/ws/alerts`;
    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onopen = () => { setConnected(true); console.log("[WS] Connected"); };
      ws.onmessage = (e) => {
        try { onMessage(JSON.parse(e.data)); } catch (_) {}
      };
      ws.onclose = () => {
        setConnected(false);
        reconnectRef.current = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
    } catch (e) { reconnectRef.current = setTimeout(connect, 5000); }
  }, [onMessage]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { connected };
}