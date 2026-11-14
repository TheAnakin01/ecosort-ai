import { MaterialCommunityIcons } from '@expo/vector-icons';
import { ActivityIndicator, Pressable, StyleSheet, Text } from 'react-native';

import { radius, theme } from '@/lib/theme';

type Variant = 'primary' | 'secondary' | 'onDark' | 'danger';

type Props = {
  label: string;
  onPress: () => void;
  variant?: Variant;
  icon?: keyof typeof MaterialCommunityIcons.glyphMap;
  disabled?: boolean;
  loading?: boolean;
  compact?: boolean;
};

const COLORS: Record<Variant, { background: string; text: string; border: string }> = {
  primary: { background: theme.brand, text: '#FFFFFF', border: theme.brand },
  secondary: { background: theme.card, text: theme.brand, border: theme.border },
  onDark: { background: theme.accent, text: theme.brandDark, border: theme.accent },
  danger: { background: theme.danger, text: '#FFFFFF', border: theme.danger },
};

export function Button({ label, onPress, variant = 'primary', icon, disabled, loading, compact }: Props) {
  const colors = COLORS[variant];
  const inactive = disabled || loading;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityState={{ disabled: inactive, busy: loading }}
      disabled={inactive}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        compact && styles.compact,
        { backgroundColor: colors.background, borderColor: colors.border },
        inactive && styles.inactive,
        pressed && styles.pressed,
      ]}>
      {loading ? (
        <ActivityIndicator color={colors.text} />
      ) : icon ? (
        <MaterialCommunityIcons name={icon} size={compact ? 18 : 22} color={colors.text} />
      ) : null}
      <Text style={[styles.label, compact && styles.compactLabel, { color: colors.text }]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: 54,
    borderRadius: radius.md,
    borderWidth: 1,
    paddingHorizontal: 20,
    flexDirection: 'row',
    gap: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  compact: { minHeight: 40, paddingHorizontal: 14, borderRadius: radius.sm, gap: 6 },
  inactive: { opacity: 0.5 },
  pressed: { opacity: 0.85, transform: [{ scale: 0.985 }] },
  label: { fontSize: 16, fontWeight: '700' },
  compactLabel: { fontSize: 14 },
});
