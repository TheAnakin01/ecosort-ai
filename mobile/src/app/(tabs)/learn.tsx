import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useState } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { CATEGORIES, CATEGORY_INFO } from '@/lib/categories';
import { radius, shadow, theme } from '@/lib/theme';
import type { Category } from '@/lib/types';

export default function LearnScreen() {
  const [open, setOpen] = useState<Category | null>('paper');

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <Text style={styles.intro}>
        Sorting waste comes down to two bins: dry waste for clean paper, plastic and metal, and wet waste for
        food and garden scraps. Tap a material to see what belongs in it.
      </Text>

      {CATEGORIES.map((category) => {
        const info = CATEGORY_INFO[category];
        const expanded = open === category;
        return (
          <View key={category} style={[styles.card, shadow]}>
            <Pressable
              onPress={() => setOpen(expanded ? null : category)}
              accessibilityRole="button"
              accessibilityState={{ expanded }}
              accessibilityLabel={`${info.label}, goes in ${info.bin}`}
              style={styles.cardHeader}>
              <View style={[styles.icon, { backgroundColor: info.soft }]}>
                <MaterialCommunityIcons name={info.icon} size={24} color={info.color} />
              </View>
              <View style={styles.cardTitleWrap}>
                <Text style={styles.cardTitle}>{info.label}</Text>
                <Text style={[styles.bin, { color: info.color }]}>{info.bin}</Text>
              </View>
              <MaterialCommunityIcons name={expanded ? 'chevron-up' : 'chevron-down'} size={24} color={theme.faint} />
            </Pressable>

            {expanded ? (
              <View style={styles.cardBody}>
                <Text style={styles.label}>Examples</Text>
                <Text style={styles.text}>{info.examples}</Text>
                <Text style={styles.label}>Common mistakes</Text>
                {info.mistakes.map((mistake) => (
                  <View key={mistake} style={styles.mistake}>
                    <MaterialCommunityIcons name="alert-circle-outline" size={18} color={theme.warning} style={styles.mistakeIcon} />
                    <Text style={[styles.text, styles.mistakeText]}>{mistake}</Text>
                  </View>
                ))}
              </View>
            ) : null}
          </View>
        );
      })}

      <View style={styles.note}>
        <MaterialCommunityIcons name="information-outline" size={18} color={theme.muted} />
        <Text style={styles.noteText}>
          This is general guidance. Local municipal rules can differ, so check what your area collects.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 8, gap: 12 },
  intro: { fontSize: 15, lineHeight: 22, color: theme.muted },
  card: { backgroundColor: theme.card, borderRadius: radius.md, overflow: 'hidden' },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 12, padding: 14 },
  icon: { width: 46, height: 46, borderRadius: 23, alignItems: 'center', justifyContent: 'center' },
  cardTitleWrap: { flex: 1 },
  cardTitle: { fontSize: 17, fontWeight: '800', color: theme.text },
  bin: { fontSize: 13, fontWeight: '700', marginTop: 1 },
  cardBody: { paddingHorizontal: 14, paddingBottom: 16, gap: 6, borderTopWidth: 1, borderTopColor: theme.border, paddingTop: 12 },
  label: { fontSize: 12, fontWeight: '700', color: theme.faint, textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 4 },
  text: { fontSize: 15, lineHeight: 22, color: theme.text },
  mistake: { flexDirection: 'row', gap: 8 },
  mistakeIcon: { marginTop: 2 },
  mistakeText: { flex: 1 },
  note: { flexDirection: 'row', gap: 8, paddingHorizontal: 4, marginTop: 4 },
  noteText: { flex: 1, fontSize: 13, lineHeight: 19, color: theme.muted },
});
