import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ClaudeRepairPanel } from '../../components/ClaudeRepairPanel';
import { ClaudeMemoryDashboard } from '../../components/ClaudeMemoryDashboard';
import { ClaudeGitAgent } from '../../components/ClaudeGitAgent';

export default function WorkspacePage() {
  return (
    <View style={styles.container}>
        <ClaudeRepairPanel />
        <ClaudeMemoryDashboard />
        <ClaudeGitAgent />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0f172a' }
});
