import { router } from 'expo-router';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { CATEGORIES, CATEGORY_INFO, theme } from '@/lib/categories';

export default function HomeScreen() {
  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.hero}>
        <Text style={styles.title}>Sort your waste with one photo</Text>
        <Text style={styles.subtitle}>
          Take a picture of your waste. EcoSort finds each item, names its material and tells you which bin it
          goes in.
        </Text>
        <Button label="Scan waste" onPress={() => router.push('/scan')} />
      </View>

      <Text style={styles.heading}>What it recognises</Text>
      {CATEGORIES.map((category) => {
        const info = CATEGORY_INFO[category];
        return (
          <View key={category} style={styles.card}>
            <View style={[styles.swatch, { backgroundColor: info.color }]} />
            <View style={styles.cardText}>
              <Text style={styles.cardTitle}>{info.label}</Text>
              <Text style={styles.cardBody}>{info.examples}</Text>
            </View>
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, gap: 12 },
  hero: { backgroundColor: theme.brandSoft, borderRadius: 16, padding: 20, gap: 12, marginBottom: 8 },
  title: { fontSize: 26, fontWeight: '700', color: theme.text },
  subtitle: { fontSize: 16, lineHeight: 23, color: theme.muted },
  heading: { fontSize: 18, fontWeight: '700', color: theme.text, marginTop: 4 },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 14,
    backgroundColor: theme.card,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: theme.border,
    padding: 14,
  },
  swatch: { width: 12, height: 40, borderRadius: 6 },
  cardText: { flex: 1 },
  cardTitle: { fontSize: 16, fontWeight: '600', color: theme.text },
  cardBody: { fontSize: 14, color: theme.muted, marginTop: 2 },
});
