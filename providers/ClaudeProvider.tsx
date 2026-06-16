import React, { createContext, useContext } from 'react';
import { memory } from '../utils/mmkv';

const ClaudeContext = createContext<any>(null);

export const ClaudeProvider = ({ children }: { children: React.ReactNode }) => {
  // Lokaler Agent-Kontext für Claude
  const executeLocalTask = async (task: string) => {
    // Hier wird ohne API-Key auf die lokalen Ressourcen zugegriffen (eigene Bridge/Shell)
    console.log(`[Claude System Hub] Ausführung: ${task}`);
    return { success: true, task };
  };

  return (
    <ClaudeContext.Provider value={{ memory, executeLocalTask }}>
      {children}
    </ClaudeContext.Provider>
  );
};

export const useClaude = () => useContext(ClaudeContext);
