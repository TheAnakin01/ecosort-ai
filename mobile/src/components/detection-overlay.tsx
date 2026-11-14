import { Image } from 'expo-image';
import { StyleSheet, Text, View } from 'react-native';

import { boxToPercent } from '@/lib/boxes';
import { CATEGORY_INFO } from '@/lib/categories';
import type { Detection } from '@/lib/types';

type Props = {
  uri: string;
  imageWidth: number;
  imageHeight: number;
  detections: Detection[];
};

/** The photo with a labelled box drawn over each detected item. */
export function DetectionOverlay({ uri, imageWidth, imageHeight, detections }: Props) {
  return (
    // The frame takes the photo's aspect ratio, so the photo fills it exactly
    // and box positions can be plain percentages.
    <View style={[styles.frame, { aspectRatio: imageWidth / imageHeight }]}>
      <Image source={{ uri }} style={StyleSheet.absoluteFill} contentFit="fill" accessibilityLabel="Scanned photo" />
      {detections.map((detection) => {
        const { label, color } = CATEGORY_INFO[detection.category];
        return (
          <View
            key={detection.id}
            style={[
              styles.box,
              boxToPercent(detection.bbox, imageWidth, imageHeight),
              { borderColor: color, borderStyle: detection.low_confidence ? 'dashed' : 'solid' },
            ]}>
            <Text style={[styles.tag, { backgroundColor: color }]} numberOfLines={1}>
              {detection.id}. {label}
              {detection.low_confidence ? ' ?' : ''}
            </Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  frame: { width: '100%', borderRadius: 12, overflow: 'hidden', backgroundColor: '#000000' },
  box: { position: 'absolute', borderWidth: 2, borderRadius: 4 },
  tag: {
    alignSelf: 'flex-start',
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '700',
    paddingHorizontal: 5,
    paddingVertical: 1,
  },
});
