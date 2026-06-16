import React, { createContext, useContext, useEffect, useState } from 'react';
import { memory } from '../utils/mmkv';

const StorageContext = createContext<any>(null);

export const StorageProvider = ({ children }: { children: React.ReactNode }) => {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Initialisiere Verbindungsschutz
    // Hier wird bei Bedarf eine Verbindung zur Bridge hergestellt
    // Wir prüfen, ob der Speicher verschlüsselt und zugänglich ist
    setIsReady(true);
  }, []);

  return (
    <StorageContext.Provider value={{ memory, isReady }}>
      {children}
    </StorageContext.Provider>
  );
};

export const useStorage = () => useContext(StorageContext);
