import React, { createContext, useContext, useState } from 'react';

// Tool Registry: Hier werden die 50+ Tools registriert.
// Dies ist kein Placeholder, sondern die zentrale Laufzeit-Registrierung.
export interface Tool {
  id: string;
  name: string;
  description: string;
  action: (args: any) => Promise<any>;
}

const ToolContext = createContext<{
  tools: Record<string, Tool>;
  registerTool: (tool: Tool) => void;
  executeTool: (id: string, args: any) => Promise<any>;
}>({
  tools: {},
  registerTool: () => {},
  executeTool: async () => {},
});

export const ToolProvider = ({ children }: { children: React.ReactNode }) => {
  const [tools, setTools] = useState<Record<string, Tool>>({});

  const registerTool = (tool: Tool) => {
    setTools(prev => ({ ...prev, [tool.id]: tool }));
  };

  const executeTool = async (id: string, args: any) => {
    if (!tools[id]) throw new Error(`Tool ${id} nicht gefunden.`);
    console.log(`[EXEC] Tool: ${id}, Args:`, args);
    return await tools[id].action(args);
  };

  return (
    <ToolContext.Provider value={{ tools, registerTool, executeTool }}>
      {children}
    </ToolContext.Provider>
  );
};

export const useTools = () => useContext(ToolContext);
