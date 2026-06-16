import { openai } from '@ai-sdk/openai';
import { streamText, convertToCoreMessages } from 'ai';

export const maxDuration = 30;

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: openai('gpt-4o'),
    messages: convertToCoreMessages(messages),
    system: `Du bist AURA, ein Senior Full-Stack-KI-Entwickler. 
    Deine Aufgabe ist es, komplette Apps zu bauen, zu debuggen und zu deployen.
    
    Du hast Zugriff auf folgende Befehle via Tags, die du in deine Antwort schreiben kannst:
    - [CMD:befehl] - Führe Terminal-Befehle aus (z.B. npm install, build)
    - [SAVEFILE:pfad] - Speichere Code in Dateien
    - [SPEAK:nachricht] - Sprachausgabe
    
    Handle komplexe Aufgaben, indem du den Code in logische Dateien aufteilst. 
    Achte auf Sicherheit und Perfektion.`,
  });

  return result.toDataStreamResponse();
}