import { MaterialCommunityIcons } from '@expo/vector-icons';
import { router, useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { ScanRow } from '@/components/scan-row';
import { checkServer, type ServerStatus } from '@/lib/api';
import { CATEGORY_INFO } from '@/lib/categories';
import { summarize } from '@/lib/history';
import { useStore } from '@/lib/store';
import { radius, shadow, theme } from '@/lib/theme';

const STATUS_TEXT: Record<ServerStatus | 'checking', { label: string; color: string; icon: 'cloud-check-outline' | 'cloud-off-outline' | 'alert-circle-outline' | 'refresh' }> = {
  checking: { label: 'Checking the server', color: theme.muted, icon: 'refresh' },
  ready: { label: 'Server connected', color: theme.success, icon: 'cloud-check-outline' },
  'no-model': { label: 'Server connected, but no trained model is loaded', color: theme.warning, icon: 'alert-circle-outline' },
  offline: { label: 'Server not reachable. Tap to retry', color: theme.danger, icon: 'cloud-off-outline' },
  'not-configured': { label: 'Preview only: no server is connected yet, so scanning is off', color: theme.warning, icon: 'cloud-off-outline' },
};

const STEPS = [
  { icon: 'camera-outline', title: 'Take a photo', body: 'Spread the items out and use good light.' },
  { icon: 'cube-scan', title: 'EcoSort finds each item', body: 'Every item gets a box and a material.' },
  { icon: 'recycle', title: 'Sort it right', body: 'See which bin each material goes in.' },
] as const;

export default function HomeScreen() {
  const { history } = useStore();
  const [status, setStatus] = useState<ServerStatus | 'checking'>('checking');
  const summary = summarize(history);
  const recent = history.slice(0, 3);

  const refreshStatus = useCallback(() => {
    let active = true;
    setStatus('checking');
    checkServer().then((result) => {
      if (active) setStatus(result);
    });
    return () => {
      active = false;
    };
  }, []);

  // Re-check every time the Home tab comes into view.
  useFocusEffect(refreshStatus);

  const statusInfo = STATUS_TEXT[status];

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.hero}>
        <Text style={styles.eyebrow}>AI waste sorting</Text>
        <Text style={styles.title}>Sort your waste with one photo</Text>
        <Text style={styles.subtitle}>
          EcoSort finds every item in the picture, names its material and tells you which bin it goes in.
        </Text>
        <Button label="Scan waste" icon="line-scan" variant="onDark" onPress={() => router.push('/scan')} />
      </View>

      <Pressable
        onPress={refreshStatus}
        accessibilityRole="button"
        accessibilityLabel={statusInfo.label}
        style={styles.status}>
        <MaterialCommunityIcons name={statusInfo.icon} size={18} color={statusInfo.color} />
        <Text style={[styles.statusText, { color: statusInfo.color }]}>{statusInfo.label}</Text>
      </Pressable>

      <View style={styles.stats}>
        <View style={[styles.stat, shadow]}>
          <Text style={styles.statNumber}>{summary.scans}</Text>
          <Text style={styles.statLabel}>Scans</Text>
        </View>
        <View style={[styles.stat, shadow]}>
          <Text style={styles.statNumber}>{summary.items}</Text>
          <Text style={styles.statLabel}>Items sorted</Text>
        </View>
        <View style={[styles.stat, shadow]}>
          <Text
            style={[styles.statNumber, summary.topCategory ? { color: CATEGORY_INFO[summary.topCategory].color } : null]}
            numberOfLines={1}
            adjustsFontSizeToFit>
            {summary.topCategory ? CATEGORY_INFO[summary.topCategory].label : '–'}
          </Text>
          <Text style={styles.statLabel}>Most common</Text>
        </View>
      </View>

      {recent.length > 0 ? (
        <>
          <View style={styles.sectionHeader}>
            <Text style={styles.heading}>Recent scans</Text>
            <Pressable onPress={() => router.push('/history')} accessibilityRole="link" hitSlop={8}>
              <Text style={styles.link}>See all</Text>
            </Pressable>
          </View>
          {recent.map((record) => (
            <ScanRow
              key={record.id}
              record={record}
              onPress={() => router.push({ pathname: '/results', params: { id: record.id } })}
            />
          ))}
        </>
      ) : null}

      <Text style={styles.heading}>How it works</Text>
      <View style={[styles.steps, shadow]}>
        {STEPS.map((step, index) => (
          <View key={step.title} style={[styles.step, index > 0 && styles.stepDivider]}>
            <View style={styles.stepIcon}>
              <MaterialCommunityIcons name={step.icon} size={22} color={theme.brand} />
            </View>
            <View style={styles.stepText}>
              <Text style={styles.stepTitle}>{step.title}</Text>
              <Text style={styles.stepBody}>{step.body}</Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 8, gap: 14 },
  hero: { backgroundColor: theme.brandDark, borderRadius: radius.lg, padding: 22, gap: 12 },
  eyebrow: { color: theme.accent, fontSize: 13, fontWeight: '700', letterSpacing: 0.6, textTransform: 'uppercase' },
  title: { fontSize: 28, lineHeight: 34, fontWeight: '800', color: '#FFFFFF' },
  subtitle: { fontSize: 15, lineHeight: 22, color: '#C9DCD3', marginBottom: 4 },
  status: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingHorizontal: 4 },
  statusText: { fontSize: 13, fontWeight: '600', flex: 1 },
  stats: { flexDirection: 'row', gap: 10 },
  stat: { flex: 1, backgroundColor: theme.card, borderRadius: radius.md, paddingVertical: 14, paddingHorizontal: 8, alignItems: 'center' },
  statNumber: { fontSize: 22, fontWeight: '800', color: theme.text },
  statLabel: { fontSize: 12, color: theme.muted, marginTop: 2 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline', marginTop: 6 },
  heading: { fontSize: 18, fontWeight: '800', color: theme.text, marginTop: 6 },
  link: { fontSize: 14, fontWeight: '700', color: theme.brand },
  steps: { backgroundColor: theme.card, borderRadius: radius.md, paddingHorizontal: 14 },
  step: { flexDirection: 'row', alignItems: 'center', gap: 14, paddingVertical: 14 },
  stepDivider: { borderTopWidth: 1, borderTopColor: theme.border },
  stepIcon: { width: 42, height: 42, borderRadius: 21, backgroundColor: theme.brandSoft, alignItems: 'center', justifyContent: 'center' },
  stepText: { flex: 1 },
  stepTitle: { fontSize: 15, fontWeight: '700', color: theme.text },
  stepBody: { fontSize: 14, color: theme.muted, marginTop: 1 },
});
