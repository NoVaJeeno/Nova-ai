import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useClaude } from '../providers/ClaudeProvider';

// Toolset für Git-Operationen direkt aus dem UI
export const ClaudeGitAgent = () => {
  const { executeLocalTask } = useClaude();

  const handleGitAction = async (action: string) => {
    const result = await executeLocalTask(`git_${action}`);
    alert(`Git ${action} erfolgreich: ${JSON.stringify(result)}`);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Git-Agent (v1.0)</Text>
      <View style={styles.row}>
        <TouchableOpacity style={styles.button} onPress={() => handleGitAction('status')}>
          <Text style={styles.buttonText}>Status</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={() => handleGitAction('commit')}>
          <Text style={styles.buttonText}>Commit</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.button} onPress={() => handleGitAction('push')}>
          <Text style={styles.buttonText}>Push</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { padding: 15, backgroundColor: '#1e293b', borderRadius: 10, margin: 10 },
  title: { color: '#fff', fontSize: 18, marginBottom: 10 },
  row: { flexDirection: 'row', justifyContent: 'space-around' },
  button: { backgroundColor: '#3b82f6', padding: 10, borderRadius: 5, width: 80 },
  buttonText: { color: '#fff', textAlign: 'center' }
});
