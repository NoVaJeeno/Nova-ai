import React, { useEffect } from 'react';
import { useTools } from '../providers/ToolProvider';
import { registerRealTools } from '../utils/bridgeTools';

export const ToolInitializer = () => {
  const { registerTool } = useTools();

  useEffect(() => {
    // Registriere alle echten Tools
    registerRealTools(registerTool);
    console.log("[AURA] Tool-System fertig initialisiert und verbunden.");
  }, [registerTool]);

  return <></>;
};
