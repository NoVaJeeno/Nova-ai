import { useState, useCallback } from 'react';
import { useTools } from '../providers/ToolProvider';

export const useChat = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { executeTool } = useTools();

  const sendMessage = useCallback(async (text: string) => {
    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: text }]);

    try {
      // Direkte Verbindung zum AURA Launcher (lokales Backend)
      const response = await fetch('http://127.0.0.1:49471/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      
      const data = await response.json();
      
      // Integration: Wenn das Backend ein Tool zurückgibt, führe es aus!
      if (data.tool_call) {
        const result = await executeTool(data.tool_call.id, data.tool_call.args);
        setMessages(prev => [...prev, { role: 'assistant', content: `Tool ausgeführt: ${result}` }]);
      } else {
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Fehler bei der Verbindung zum Core." }]);
    } finally {
      setIsLoading(false);
    }
  }, [executeTool]);

  return { messages, sendMessage, isLoading };
};
