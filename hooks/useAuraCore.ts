import { useState, useEffect } from 'react';

// Zentrale Schnittstelle für das AURA Core-System (lokal)
// Da wir keine externe Bridge mehr benötigen, agiert der Launcher als Heartbeat
export const useAuraCore = () => {
  const [status, setStatus] = useState<'online' | 'offline' | 'loading'>('loading');

  const checkCoreStatus = async () => {
    try {
      // Direkter Abruf beim Launcher (Mainframe)
      const response = await fetch('http://127.0.0.1:49471/health', {
        method: 'GET',
        headers: { 'Accept': 'application/json' },
      });
      if (response.ok) {
        setStatus('online');
      } else {
        setStatus('offline');
      }
    } catch (e) {
      setStatus('offline');
    }
  };

  useEffect(() => {
    checkCoreStatus();
    const interval = setInterval(checkCoreStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return { status };
};
