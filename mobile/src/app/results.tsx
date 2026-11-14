import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Redirect, router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { DetectionOverlay } from '@/components/detection-overlay';
import { CATEGORIES, CATEGORY_INFO } from '@/lib/categories';
import { formatWhen } from '@/lib/history';
import { useStore } from '@/lib/store';
import { radius, shadow, theme } from '@/lib/theme';

export default function ResultsScreen() {
  const { id } = useLocalSearchParams<{ id?: string }>();
  const { loaded, history } = useStore();
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const record = history.find((item) => item.id === id);

  if (!record) {
    // Still reading saved scans: wait. Otherwise the scan is gone (deleted,
    // or a stale link), so send the user somewhere useful.
    return loaded ? <Redirect href="/" /> : null;
  }

  const { response, guidance } = record;
  const itemWord = response.total_objects === 1 ? 'item' : 'items';

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <DetectionOverlay
        uri={record.photoUri}
        imageWidth={response.image_width}
        imageHeight={response.image_height}
        detections={response.detections}
        selectedId={selectedId}
        onSelect={setSelectedId}
      />

      <View style={styles.titleRow}>
        <Text style={styles.title}>
          {response.total_objects === 0 ? 'Nothing found' : `${response.total_objects} ${itemWord} found`}
        </Text>
        <Text style={styles.when}>{formatWhen(record.createdAt)}</Text>
      </View>

      {response.message ? (
        <View style={styles.notice}>
          <MaterialCommunityIcons name="alert-circle-outline" size={20} color={theme.warning} />
          <Text style={styles.noticeText}>{response.message}</Text>
        </View>
      ) : null}

      {response.total_objects > 0 ? (
        <View style={styles.counts}>
          {CATEGORIES.map((category) => {
            const info = CATEGORY_INFO[category];
            const count = response.counts[category];
            return (
              <View key={category} style={[styles.count, shadow, count === 0 && styles.countEmpty]}>
                <MaterialCommunityIcons name={info.icon} size={20} color={info.color} />
                <Text style={[styles.countNumber, { color: info.color }]}>{count}</Text>
                <Text style={styles.countLabel}>{info.label}</Text>
              </View>
            );
          })}
        </View>
      ) : null}

      {response.detections.length > 0 ? (
        <>
          <Text style={styles.heading}>Items</Text>
          <Text style={styles.hint}>Tap an item or a box to highlight it.</Text>
        </>
      ) : null}
      {response.detections.map((detection) => {
        const info = CATEGORY_INFO[detection.category];
        const selected = detection.id === selectedId;
        const percent = Math.round(detection.confidence * 100);
        return (
          <Pressable
            key={detection.id}
            onPress={() => setSelectedId(selected ? null : detection.id)}
            accessibilityRole="button"
            accessibilityState={{ selected }}
            accessibilityLabel={`Item ${detection.id}, ${info.label}, ${percent} percent sure`}
            style={[styles.item, shadow, selected && { borderColor: info.color }]}>
            <View style={[styles.itemBadge, { backgroundColor: info.color }]}>
              <Text style={styles.itemBadgeText}>{detection.id}</Text>
            </View>
            <View style={styles.itemBody}>
              <View style={styles.itemTop}>
                <Text style={styles.itemTitle}>{info.label}</Text>
                <Text style={styles.itemPercent}>
                  {percent}% sure{detection.low_confidence ? ' · uncertain' : ''}
                </Text>
              </View>
              <View style={styles.barTrack}>
                <View style={[styles.barFill, { width: `${percent}%`, backgroundColor: info.color }]} />
              </View>
            </View>
          </Pressable>
        );
      })}

      {guidance.length > 0 ? <Text style={styles.heading}>How to sort it</Text> : null}
      {guidance.map((entry) => {
        const info = CATEGORY_INFO[entry.category];
        return (
          <View key={entry.category} style={[styles.guide, shadow]}>
            <View style={styles.guideHeader}>
              <View style={[styles.guideIcon, { backgroundColor: info.soft }]}>
                <MaterialCommunityIcons name={info.icon} size={20} color={info.color} />
              </View>
              <Text style={styles.guideTitle}>{info.label}</Text>
              <View style={[styles.binBadge, { backgroundColor: info.soft }]}>
                <Text style={[styles.binText, { color: info.color }]}>{entry.bin}</Text>
              </View>
            </View>
            {entry.tips.map((tip) => (
              <View key={tip} style={styles.tip}>
                <MaterialCommunityIcons name="check-circle-outline" size={18} color={theme.success} style={styles.tipIcon} />
                <Text style={styles.tipText}>{tip}</Text>
              </View>
            ))}
          </View>
        );
      })}
      {guidance.length > 0 ? <Text style={styles.disclaimer}>{guidance[0].disclaimer}</Text> : null}

      <Button label="Scan another photo" icon="line-scan" onPress={() => router.replace('/scan')} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 8, gap: 12 },
  titleRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline', marginTop: 4 },
  title: { fontSize: 22, fontWeight: '800', color: theme.text },
  when: { fontSize: 13, color: theme.muted },
  notice: { flexDirection: 'row', gap: 10, backgroundColor: theme.warningSoft, borderRadius: radius.md, padding: 14 },
  noticeText: { flex: 1, color: theme.warning, fontSize: 15, lineHeight: 21 },
  counts: { flexDirection: 'row', gap: 8 },
  count: { flex: 1, alignItems: 'center', backgroundColor: theme.card, borderRadius: radius.md, paddingVertical: 12, gap: 2 },
  countEmpty: { opacity: 0.45 },
  countNumber: { fontSize: 22, fontWeight: '800' },
  countLabel: { fontSize: 12, color: theme.muted },
  heading: { fontSize: 18, fontWeight: '800', color: theme.text, marginTop: 8 },
  hint: { fontSize: 13, color: theme.muted, marginTop: -8 },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: theme.card,
    borderRadius: radius.md,
    borderWidth: 2,
    borderColor: 'transparent',
    padding: 12,
  },
  itemBadge: { width: 30, height: 30, borderRadius: 15, alignItems: 'center', justifyContent: 'center' },
  itemBadgeText: { color: '#FFFFFF', fontWeight: '800', fontSize: 14 },
  itemBody: { flex: 1, gap: 8 },
  itemTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' },
  itemTitle: { fontSize: 16, fontWeight: '700', color: theme.text },
  itemPercent: { fontSize: 13, color: theme.muted },
  barTrack: { height: 6, borderRadius: 3, backgroundColor: theme.border, overflow: 'hidden' },
  barFill: { height: 6, borderRadius: 3 },
  guide: { backgroundColor: theme.card, borderRadius: radius.md, padding: 14, gap: 8 },
  guideHeader: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 2 },
  guideIcon: { width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center' },
  guideTitle: { flex: 1, fontSize: 16, fontWeight: '800', color: theme.text },
  binBadge: { borderRadius: radius.pill, paddingHorizontal: 10, paddingVertical: 4 },
  binText: { fontSize: 13, fontWeight: '700' },
  tip: { flexDirection: 'row', gap: 8 },
  tipIcon: { marginTop: 2 },
  tipText: { flex: 1, fontSize: 15, lineHeight: 21, color: theme.text },
  disclaimer: { fontSize: 13, lineHeight: 19, color: theme.muted },
});
