import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAuraCore } from '../hooks/useAuraCore';

export const AuraStatusBanner = () => {
  const { status } = useAuraCore();

  return (
    <View style={[styles.container, { backgroundColor: status === 'online' ? '#22c55e' : '#ef4444' }]}>
      <Text style={styles.text}>AURA Core: {status.toUpperCase()}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    padding: 8,
    borderRadius: 8,
    margin: 10,
    alignItems: 'center',
  },
  text: {
    color: '#ffffff',
    fontWeight: 'bold',
    fontSize: 12,
  },
});
