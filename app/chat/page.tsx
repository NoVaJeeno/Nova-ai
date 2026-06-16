import React from 'react';
import { View, TextInput, Button, FlatList, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useChat } from '../../hooks/useChat';
import { AuraStatusBanner } from '../../components/AuraStatusBanner';

export default function ChatPage() {
  const { messages, sendMessage, isLoading } = useChat();
  const [input, setInput] = React.useState('');

  const onSend = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput('');
  };

  return (
    <View style={styles.container}>
      <AuraStatusBanner />
      <FlatList
        data={messages}
        keyExtractor={(_, i) => i.toString()}
        renderItem={({ item }) => (
          <View style={styles.message}>
            <Text style={styles.role}>{item.role === 'user' ? 'Du' : 'AURA'}</Text>
            <Text>{item.content}</Text>
          </View>
        )}
      />
      {isLoading && <ActivityIndicator size="large" color="#7c3aed" />}
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={input}
          onChangeText={setInput}
          placeholder="Schreibe eine Nachricht an AURA..."
        />
        <Button title="Senden" onPress={onSend} color="#7c3aed" />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 10, backgroundColor: '#1a1a2e' },
  message: { marginVertical: 5, padding: 10, backgroundColor: '#f0f0f0', borderRadius: 8 },
  role: { fontWeight: 'bold' },
  inputContainer: { flexDirection: 'row', padding: 10 },
  input: { flex: 1, backgroundColor: '#fff', padding: 10, borderRadius: 5, marginRight: 10 },
});
