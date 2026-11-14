import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import { useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';

import { boxToPercent } from '@/lib/boxes';
import { CATEGORY_INFO } from '@/lib/categories';
import { radius, theme } from '@/lib/theme';
import type { Detection } from '@/lib/types';

type Props = {
  uri: string;
  imageWidth: number;
  imageHeight: number;
  detections: Detection[];
  selectedId: number | null;
  onSelect: (id: number | null) => void;
};

/** The photo with a labelled, tappable box drawn over each detected item. */
export function DetectionOverlay({ uri, imageWidth, imageHeight, detections, selectedId, onSelect }: Props) {
  const [failed, setFailed] = useState(false);

  if (failed) {
    return (
      <View style={[styles.frame, styles.missing, { aspectRatio: imageWidth / imageHeight }]}>
        <MaterialCommunityIcons name="image-off-outline" size={32} color={theme.faint} />
        <Text style={styles.missingText}>The photo for this scan is no longer available.</Text>
      </View>
    );
  }

  return (
    // The frame takes the photo's aspect ratio, so the photo fills it exactly
    // and box positions can be plain percentages.
    <Pressable
      style={[styles.frame, { aspectRatio: imageWidth / imageHeight }]}
      onPress={() => onSelect(null)}
      accessibilityLabel="Scanned photo">
      <Image source={{ uri }} style={StyleSheet.absoluteFill} contentFit="fill" onError={() => setFailed(true)} />
      {detections.map((detection) => {
        const { label, color } = CATEGORY_INFO[detection.category];
        const selected = detection.id === selectedId;
        const dimmed = selectedId !== null && !selected;
        return (
          <Pressable
            key={detection.id}
            onPress={() => onSelect(selected ? null : detection.id)}
            accessibilityRole="button"
            accessibilityLabel={`Item ${detection.id}, ${detection.low_confidence ? 'possibly ' : ''}${label}`}
            accessibilityState={{ selected }}
            style={[
              styles.box,
              boxToPercent(detection.bbox, imageWidth, imageHeight),
              {
                borderColor: color,
                borderStyle: detection.low_confidence ? 'dashed' : 'solid',
                borderWidth: selected ? 4 : 2,
                opacity: dimmed ? 0.35 : 1,
              },
            ]}>
            {/* The tag may be wider than a small box, so it sits in its own
                layer and is allowed to spill past the box's right edge. */}
            <View style={styles.tagLayer} pointerEvents="none">
              <Text style={[styles.tag, { backgroundColor: color }]} numberOfLines={1}>
                {detection.id} {label}
                {detection.low_confidence ? ' ?' : ''}
              </Text>
            </View>
          </Pressable>
        );
      })}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  frame: { width: '100%', borderRadius: radius.lg, overflow: 'hidden', backgroundColor: '#0B1410' },
  missing: {
    backgroundColor: theme.card,
    borderWidth: 1,
    borderColor: theme.border,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 24,
  },
  missingText: { color: theme.muted, fontSize: 14, textAlign: 'center' },
  box: { position: 'absolute', borderRadius: 6 },
  tagLayer: { position: 'absolute', top: 0, left: 0, width: 160 },
  tag: {
    alignSelf: 'flex-start',
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderBottomRightRadius: 6,
  },
});
