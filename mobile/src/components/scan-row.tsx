import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { CATEGORIES, CATEGORY_INFO } from '@/lib/categories';
import { formatWhen } from '@/lib/history';
import { radius, shadow, theme } from '@/lib/theme';
import type { ScanRecord } from '@/lib/types';

type Props = {
  record: ScanRecord;
  onPress: () => void;
  /** Shown at the right edge, for example a delete button. */
  trailing?: React.ReactNode;
};

/** One past scan: thumbnail, when it happened, and what was found. */
export function ScanRow({ record, onPress, trailing }: Props) {
  const { response } = record;
  const found = CATEGORIES.filter((category) => response.counts[category] > 0);
  const itemWord = response.total_objects === 1 ? 'item' : 'items';

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={`Scan from ${formatWhen(record.createdAt)}, ${response.total_objects} ${itemWord}`}
      style={({ pressed }) => [styles.row, shadow, pressed && styles.pressed]}>
      <Image source={{ uri: record.photoUri }} style={styles.thumb} contentFit="cover" />
      <View style={styles.body}>
        <Text style={styles.title}>
          {response.total_objects === 0 ? 'Nothing found' : `${response.total_objects} ${itemWord}`}
        </Text>
        <Text style={styles.when}>{formatWhen(record.createdAt)}</Text>
        {found.length > 0 ? (
          <View style={styles.chips}>
            {found.map((category) => (
              <View key={category} style={[styles.chip, { backgroundColor: CATEGORY_INFO[category].soft }]}>
                <Text style={[styles.chipText, { color: CATEGORY_INFO[category].color }]}>
                  {response.counts[category]} {CATEGORY_INFO[category].label}
                </Text>
              </View>
            ))}
          </View>
        ) : null}
      </View>
      {trailing ?? <MaterialCommunityIcons name="chevron-right" size={24} color={theme.faint} />}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: theme.card,
    borderRadius: radius.md,
    padding: 10,
  },
  pressed: { opacity: 0.85 },
  thumb: { width: 64, height: 64, borderRadius: radius.sm, backgroundColor: theme.brandSoft },
  body: { flex: 1, gap: 2 },
  title: { fontSize: 16, fontWeight: '700', color: theme.text },
  when: { fontSize: 13, color: theme.muted },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 4 },
  chip: { borderRadius: radius.pill, paddingHorizontal: 8, paddingVertical: 2 },
  chipText: { fontSize: 12, fontWeight: '700' },
});
