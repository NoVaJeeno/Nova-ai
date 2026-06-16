import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import util from 'util';

const execPromise = util.promisify(exec);

export async function POST(req: Request) {
  const { command } = await req.json();

  if (!command) {
    return NextResponse.json({ error: 'Kein Befehl angegeben' }, { status: 400 });
  }

  // Sicherheits-Filter: Erlaube nur bestimmte Befehle
  const allowed = ['npm install', 'npm run build', 'ls -la', 'pwd'];
  if (!allowed.some(cmd => command.startsWith(cmd))) {
    return NextResponse.json({ error: 'Befehl nicht erlaubt' }, { status: 403 });
  }

  try {
    const { stdout, stderr } = await execPromise(command);
    return NextResponse.json({ stdout, stderr });
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}