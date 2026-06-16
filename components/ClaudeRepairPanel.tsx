import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useClaude } from '../providers/ClaudeProvider';

// Der File-Scanner durchsucht deine lokalen Projekte nach Fehlern
export const ClaudeRepairPanel = () => {
  const { executeLocalTask } = useClaude();

  const scanProject = async () => {
    // Ruft echten Backend-Scanner auf
    const result = await executeLocalTask('scan_project_logs');
    alert('Scan abgeschlossen: ' + JSON.stringify(result));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>System Health & Repair</Text>
      <TouchableOpacity style={styles.button} onPress={scanProject}>
        <Text style={styles.buttonText}>System & Logs scannen</Text>
      </TouchableOpacity>
      <ScrollView style={styles.log}>
        <Text style={styles.logText}>Warte auf Scan-Befehl...</Text>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 15, backgroundColor: '#1e293b', borderRadius: 10, margin: 10 },
  title: { color: '#fff', fontSize: 18, marginBottom: 10 },
  button: { backgroundColor: '#3b82f6', padding: 10, borderRadius: 5 },
  buttonText: { color: '#fff', textAlign: 'center' },
  log: { height: 100, backgroundColor: '#000', marginTop: 10, padding: 5 },
  logText: { color: '#22c55e', fontFamily: 'monospace' }
});
