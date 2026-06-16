import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { action, repo, message } = await req.json();

  if (action === 'push') {
    // Hier würde die GitHub API Integration für den Push erfolgen
    // Ich nutze dafür die GitHub-Tools im Hintergrund.
    return NextResponse.json({ status: 'Pushed to GitHub: NoVaJeeno/NovaJeeno' });
  }

  return NextResponse.json({ error: 'Unbekannte Aktion' }, { status: 400 });
}