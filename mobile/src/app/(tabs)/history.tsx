import { MaterialCommunityIcons } from '@expo/vector-icons';
import { router } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { ScanRow } from '@/components/scan-row';
import { useStore } from '@/lib/store';
import { radius, theme } from '@/lib/theme';

export default function HistoryScreen() {
  const { loaded, history, removeScan, clearHistory } = useStore();
  // Deleting takes two taps: the first arms it, the second confirms.
  const [armedId, setArmedId] = useState<string | null>(null);
  const [clearArmed, setClearArmed] = useState(false);

  if (!loaded) {
    return null;
  }

  if (history.length === 0) {
    return (
      <View style={styles.empty}>
        <View style={styles.emptyIcon}>
          <MaterialCommunityIcons name="history" size={36} color={theme.brand} />
        </View>
        <Text style={styles.emptyTitle}>No scans yet</Text>
        <Text style={styles.emptyBody}>
          Your scans and their photos are saved on this device only. Nothing is stored on a server.
        </Text>
        <Button label="Scan waste" icon="line-scan" onPress={() => router.push('/scan')} />
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.count}>
          {history.length} {history.length === 1 ? 'scan' : 'scans'} saved on this device only
        </Text>
        {clearArmed ? (
          <View style={styles.confirm}>
            <Button label="Cancel" variant="secondary" compact onPress={() => setClearArmed(false)} />
            <Button
              label="Delete all"
              variant="danger"
              compact
              onPress={() => {
                setClearArmed(false);
                clearHistory();
              }}
            />
          </View>
        ) : (
          <Button label="Clear all" variant="secondary" icon="delete-outline" compact onPress={() => setClearArmed(true)} />
        )}
      </View>

      {history.map((record) => (
        <ScanRow
          key={record.id}
          record={record}
          onPress={() => router.push({ pathname: '/results', params: { id: record.id } })}
          trailing={
            armedId === record.id ? (
              <View style={styles.confirm}>
                <Button label="Keep" variant="secondary" compact onPress={() => setArmedId(null)} />
                <Button
                  label="Delete"
                  variant="danger"
                  compact
                  onPress={() => {
                    setArmedId(null);
                    removeScan(record.id);
                  }}
                />
              </View>
            ) : (
              <Pressable
                onPress={() => setArmedId(record.id)}
                accessibilityRole="button"
                accessibilityLabel="Delete this scan"
                hitSlop={8}
                style={styles.deleteButton}>
                <MaterialCommunityIcons name="delete-outline" size={22} color={theme.muted} />
              </Pressable>
            )
          }
        />
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 8, gap: 12 },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 10, minHeight: 40 },
  count: { fontSize: 14, color: theme.muted, flex: 1 },
  confirm: { flexDirection: 'row', gap: 6 },
  deleteButton: { width: 40, height: 40, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
  empty: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 32, gap: 10 },
  emptyIcon: { width: 72, height: 72, borderRadius: 36, backgroundColor: theme.brandSoft, alignItems: 'center', justifyContent: 'center' },
  emptyTitle: { fontSize: 20, fontWeight: '800', color: theme.text },
  emptyBody: { fontSize: 15, lineHeight: 22, color: theme.muted, textAlign: 'center', marginBottom: 8 },
});
