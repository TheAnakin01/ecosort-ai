import { useEffect, useState } from 'react';
import { Animated, Easing, Platform, StyleSheet, View } from 'react-native';

import { theme } from '@/lib/theme';

/** A bar that sweeps up and down over the photo while it is being scanned. */
export function ScanLine({ height }: { height: number }) {
  const [progress] = useState(() => new Animated.Value(0));

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(progress, {
          toValue: 1,
          duration: 1400,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: Platform.OS !== 'web',
        }),
        Animated.timing(progress, {
          toValue: 0,
          duration: 1400,
          easing: Easing.inOut(Easing.quad),
          useNativeDriver: Platform.OS !== 'web',
        }),
      ]),
    );
    loop.start();
    return () => loop.stop();
  }, [progress]);

  const translateY = progress.interpolate({ inputRange: [0, 1], outputRange: [0, Math.max(height - 4, 0)] });

  return (
    <View style={styles.cover} pointerEvents="none">
      <Animated.View style={[styles.line, { transform: [{ translateY }] }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  cover: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(11, 59, 44, 0.35)' },
  line: { height: 4, backgroundColor: theme.accent, boxShadow: '0 0 16px 4px rgba(185, 242, 161, 0.7)' },
});
