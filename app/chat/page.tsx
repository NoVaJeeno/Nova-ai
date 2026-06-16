"use client";

import { useState } from 'react';
import { useChat } from 'ai/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();
  const [output, setOutput] = useState('');

  const executeCommand = async (command: string) => {
    const res = await fetch('/api/exec', {
      method: 'POST',
      body: JSON.stringify({ command }),
    });
    const data = await res.json();
    setOutput(data.stdout || data.stderr || data.error);
  };

  return (
    <div className="flex h-screen bg-gray-900 text-white">
      <div className="w-2/3 flex flex-col p-4 border-r border-gray-700">
        <div className="flex-1 overflow-y-auto mb-4">
          {messages.map(m => (
            <div key={m.id} className="mb-4">
              <strong>{m.role === 'user' ? 'Du' : 'AURA'}:</strong> {m.content}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            className="flex-1 p-2 bg-gray-800 rounded border border-gray-600"
            value={input}
            onChange={handleInputChange}
            placeholder="Beschreibe eine App..."
          />
          <button className="bg-purple-600 px-4 py-2 rounded">Senden</button>
        </form>
      </div>
      <div className="w-1/3 p-4">
        <h2 className="font-bold mb-2">Code Execution & DevTools</h2>
        <div className="space-y-2">
          <button onClick={() => executeCommand('npm install')} className="w-full bg-blue-600 p-2 rounded">npm install</button>
          <button onClick={() => executeCommand('ls -la')} className="w-full bg-gray-700 p-2 rounded">ls -la</button>
        </div>
        <pre className="mt-4 p-2 bg-black rounded text-xs overflow-x-auto">{output}</pre>
      </div>
    </div>
  );
}