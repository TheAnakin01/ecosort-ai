import { Redirect, router } from 'expo-router';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { DetectionOverlay } from '@/components/detection-overlay';
import { CATEGORIES, CATEGORY_INFO, theme } from '@/lib/categories';
import { useScan } from '@/lib/scan-context';

export default function ResultsScreen() {
  const { result } = useScan();

  // Opened without a scan, for example after a page reload on web.
  if (!result) {
    return <Redirect href="/scan" />;
  }

  const { photo, response, guidance } = result;
  const itemWord = response.total_objects === 1 ? 'item' : 'items';

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <DetectionOverlay
        uri={photo.uri}
        imageWidth={response.image_width}
        imageHeight={response.image_height}
        detections={response.detections}
      />

      <Text style={styles.heading}>
        {response.total_objects === 0 ? 'Nothing found' : `${response.total_objects} ${itemWord} found`}
      </Text>

      {response.message ? (
        <View style={styles.notice}>
          <Text style={styles.noticeText}>{response.message}</Text>
        </View>
      ) : null}

      {response.total_objects > 0 ? (
        <View style={styles.counts}>
          {CATEGORIES.map((category) => (
            <View key={category} style={styles.count}>
              <Text style={[styles.countNumber, { color: CATEGORY_INFO[category].color }]}>
                {response.counts[category]}
              </Text>
              <Text style={styles.countLabel}>{CATEGORY_INFO[category].label}</Text>
            </View>
          ))}
        </View>
      ) : null}

      {response.detections.length > 0 ? <Text style={styles.heading}>Items</Text> : null}
      {response.detections.map((detection) => (
        <View key={detection.id} style={styles.row}>
          <Text style={styles.rowTitle}>
            {detection.id}. {CATEGORY_INFO[detection.category].label}
          </Text>
          <Text style={styles.rowDetail}>
            {Math.round(detection.confidence * 100)}% sure{detection.low_confidence ? ' · uncertain' : ''}
          </Text>
        </View>
      ))}

      {guidance.length > 0 ? <Text style={styles.heading}>How to sort it</Text> : null}
      {guidance.map((entry) => (
        <View key={entry.category} style={styles.card}>
          <Text style={[styles.cardTitle, { color: CATEGORY_INFO[entry.category].color }]}>
            {CATEGORY_INFO[entry.category].label} → {entry.bin}
          </Text>
          {entry.tips.map((tip) => (
            <Text key={tip} style={styles.tip}>
              • {tip}
            </Text>
          ))}
        </View>
      ))}
      {guidance.length > 0 ? <Text style={styles.disclaimer}>{guidance[0].disclaimer}</Text> : null}

      <Button label="Scan another photo" onPress={() => router.back()} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, gap: 12 },
  heading: { fontSize: 18, fontWeight: '700', color: theme.text, marginTop: 4 },
  notice: { backgroundColor: theme.warningSoft, borderRadius: 12, padding: 14 },
  noticeText: { color: theme.warning, fontSize: 15, lineHeight: 21 },
  counts: {
    flexDirection: 'row',
    backgroundColor: theme.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
    paddingVertical: 14,
  },
  count: { flex: 1, alignItems: 'center' },
  countNumber: { fontSize: 24, fontWeight: '700' },
  countLabel: { fontSize: 13, color: theme.muted, marginTop: 2 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: theme.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
    padding: 14,
  },
  rowTitle: { fontSize: 16, fontWeight: '600', color: theme.text },
  rowDetail: { fontSize: 14, color: theme.muted },
  card: {
    backgroundColor: theme.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
    padding: 14,
    gap: 6,
  },
  cardTitle: { fontSize: 16, fontWeight: '700' },
  tip: { fontSize: 15, lineHeight: 21, color: theme.text },
  disclaimer: { fontSize: 13, lineHeight: 19, color: theme.muted },
});
