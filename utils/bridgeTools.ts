import { useTools } from '../providers/ToolProvider';
import { useAuth } from '../providers/AuthProvider';
import axios from 'axios';

// BRIDGE TOOLS: Echte Kommunikation mit dem Server via Rork-Bridge
// Alle Aufrufe gehen real an 100.79.19.27:49152 (Tailscale)

export const registerRealTools = (registerTool: any) => {
  
  // REAL: Terminal Tool
  registerTool({
    id: 'terminal_exec',
    name: 'Terminal Executor',
    description: 'Führt echte Shell-Befehle auf dem Server aus.',
    action: async ({ cmd }: { cmd: string }) => {
      const { checkConnection } = useAuth(); // Theoretisch, wir brauchen hier den Token
      const response = await axios.post('http://100.79.19.27:49152/exec', { cmd }, {
        headers: { Authorization: 'Bearer rork-bridge-2026' }
      });
      return response.data;
    }
  });

  // REAL: Datei Schreiben
  registerTool({
    id: 'file_write',
    name: 'File Writer',
    description: 'Schreibt Dateien direkt auf das Ziel-Filesystem.',
    action: async ({ path, content }: { path: string, content: string }) => {
      const response = await axios.post('http://100.79.19.27:49152/write', { path, content }, {
        headers: { Authorization: 'Bearer rork-bridge-2026' }
      });
      return response.data;
    }
  });
};
