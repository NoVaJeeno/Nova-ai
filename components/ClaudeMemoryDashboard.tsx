import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { useClaude } from '../providers/ClaudeProvider';

// Visualisiert den dauerhaften Arbeitsspeicher (Memory V2)
export const ClaudeMemoryDashboard = () => {
  const { memory } = useClaude();
  const [memories, setMemories] = useState<any[]>([]);

  useEffect(() => {
    // Echtzeit-Sync mit MMKV-basiertem Gedächtnis
    const refresh = () => {
      const stored = memory.getString('aura_memory_v2');
      setMemories(stored ? JSON.parse(stored) : []);
    };
    refresh();
  }, [memory]);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>System-Gedächtnis (Memory V2)</Text>
      <FlatList
        data={memories}
        keyExtractor={(item, index) => index.toString()}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.memoryText}>{item.content}</Text>
            <Text style={styles.tag}>{item.tag}</Text>
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 15, backgroundColor: '#0f172a', borderRadius: 10, margin: 10 },
  title: { color: '#fff', fontSize: 18, marginBottom: 10 },
  card: { backgroundColor: '#334155', padding: 10, borderRadius: 5, marginBottom: 5 },
  memoryText: { color: '#e2e8f0' },
  tag: { color: '#fbbf24', fontSize: 10, marginTop: 5 }
});
