import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useClaude } from '../providers/ClaudeProvider';

export const ClaudeStatusBanner = () => {
  const { memory } = useClaude();

  return (
    <View style={styles.container}>
      <Text style={styles.text}>Claude System Hub: ONLINE</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 10,
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    marginVertical: 10,
  },
  text: {
    color: '#ffffff',
    fontWeight: 'bold',
    textAlign: 'center',
  },
});
