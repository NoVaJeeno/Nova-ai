import { MMKV } from 'react-native-mmkv';

// Sicherer Speicher für die Claude-Ultimate-App
export const memory = new MMKV({
  id: 'claude_system_storage',
  encryptionKey: 'claude_ultimate_secure_2026',
});

export const savePersistent = (key: string, value: any) => {
  memory.set(key, JSON.stringify(value));
};

export const getPersistent = <T>(key: string): T | null => {
  const value = memory.getString(key);
  return value ? JSON.parse(value) : null;
};
