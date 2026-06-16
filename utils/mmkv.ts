import { MMKV } from 'react-native-mmkv';

// Speicherkonfiguration für Ultimate AURA
export const memory = new MMKV({
  id: 'ultimate_aura_storage',
  encryptionKey: 'aura_secret_2026', // Härtung gegen Hacker
});

export const savePersistent = (key: string, value: any) => {
  memory.set(key, JSON.stringify(value));
};

export const getPersistent = <T>(key: string): T | null => {
  const value = memory.getString(key);
  return value ? JSON.parse(value) : null;
};
