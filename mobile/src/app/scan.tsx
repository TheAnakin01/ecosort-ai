import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Image } from 'expo-image';
import * as ImagePicker from 'expo-image-picker';
import { router } from 'expo-router';
import { useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { ScanLine } from '@/components/scan-line';
import { ApiError, scanPhoto } from '@/lib/api';
import { keepPhoto } from '@/lib/photo-store';
import { useStore } from '@/lib/store';
import { radius, theme } from '@/lib/theme';
import type { Photo } from '@/lib/types';

// Lower quality keeps uploads small and fast; the detector resizes to 640px anyway.
const PICKER_OPTIONS: ImagePicker.ImagePickerOptions = { mediaTypes: 'images', quality: 0.7 };

const TIPS = ['Spread the items out', 'Use good light', 'Keep everything in the frame'];

export default function ScanScreen() {
  const { addScan } = useStore();
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewHeight, setPreviewHeight] = useState(0);

  async function pick(source: 'camera' | 'gallery') {
    setError(null);
    try {
      if (source === 'camera') {
        const permission = await ImagePicker.requestCameraPermissionsAsync();
        if (!permission.granted) {
          setError('Camera access is off. Allow it in your phone settings, or choose a photo from the gallery.');
          return;
        }
      }
      const picked =
        source === 'camera'
          ? await ImagePicker.launchCameraAsync(PICKER_OPTIONS)
          : await ImagePicker.launchImageLibraryAsync(PICKER_OPTIONS);
      if (!picked.canceled) {
        const asset = picked.assets[0];
        setPhoto({ uri: asset.uri, mimeType: asset.mimeType, fileName: asset.fileName, file: asset.file });
      }
    } catch {
      setError(
        source === 'camera'
          ? 'The camera could not be opened on this device. Choose a photo from the gallery.'
          : 'The gallery could not be opened. Try again.',
      );
    }
  }

  async function scan() {
    if (!photo) return;
    setError(null);
    setScanning(true);
    try {
      const { response, guidance } = await scanPhoto(photo);
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      // If the photo cannot be copied, keep the original location: the result
      // still shows now, the picture may just be missing from history later.
      const photoUri = await keepPhoto(photo.uri, id).catch(() => photo.uri);
      await addScan({ id, createdAt: new Date().toISOString(), photoUri, response, guidance });
      router.replace({ pathname: '/results', params: { id } });
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Something went wrong. Try again.');
      setScanning(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.preview} onLayout={(event) => setPreviewHeight(event.nativeEvent.layout.height)}>
        {photo ? (
          <Image source={{ uri: photo.uri }} style={StyleSheet.absoluteFill} contentFit="cover" accessibilityLabel="Selected photo" />
        ) : (
          <View style={styles.placeholder}>
            <View style={styles.placeholderIcon}>
              <MaterialCommunityIcons name="camera-outline" size={34} color={theme.brand} />
            </View>
            <Text style={styles.placeholderTitle}>Add a photo of your waste</Text>
            {TIPS.map((tip) => (
              <View key={tip} style={styles.tip}>
                <MaterialCommunityIcons name="check-circle-outline" size={16} color={theme.success} />
                <Text style={styles.tipText}>{tip}</Text>
              </View>
            ))}
          </View>
        )}
        {scanning ? <ScanLine height={previewHeight} /> : null}
      </View>

      {scanning ? <Text style={styles.scanningText}>Looking for waste items</Text> : null}

      {error ? (
        <View style={styles.error} accessibilityRole="alert">
          <MaterialCommunityIcons name="alert-circle-outline" size={20} color={theme.danger} />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      ) : null}

      {photo ? (
        <>
          <Button label={scanning ? 'Scanning' : 'Scan this photo'} icon="line-scan" onPress={scan} loading={scanning} />
          <View style={styles.pair}>
            <View style={styles.pairItem}>
              <Button label="Retake" icon="camera-retake-outline" variant="secondary" onPress={() => pick('camera')} disabled={scanning} />
            </View>
            <View style={styles.pairItem}>
              <Button label="Gallery" icon="image-multiple-outline" variant="secondary" onPress={() => pick('gallery')} disabled={scanning} />
            </View>
          </View>
        </>
      ) : (
        <>
          <Button label="Take a photo" icon="camera-outline" onPress={() => pick('camera')} />
          <Button label="Choose from gallery" icon="image-multiple-outline" variant="secondary" onPress={() => pick('gallery')} />
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 8, gap: 12 },
  preview: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: radius.lg,
    overflow: 'hidden',
    backgroundColor: theme.card,
    borderWidth: 1,
    borderColor: theme.border,
  },
  placeholder: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24, gap: 8 },
  placeholderIcon: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: theme.brandSoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 4,
  },
  placeholderTitle: { fontSize: 18, fontWeight: '800', color: theme.text, marginBottom: 6 },
  tip: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  tipText: { fontSize: 15, color: theme.muted },
  scanningText: { textAlign: 'center', fontSize: 15, fontWeight: '600', color: theme.brand },
  error: { flexDirection: 'row', gap: 10, backgroundColor: theme.dangerSoft, borderRadius: radius.md, padding: 14 },
  errorText: { flex: 1, color: theme.danger, fontSize: 15, lineHeight: 21 },
  pair: { flexDirection: 'row', gap: 12 },
  pairItem: { flex: 1 },
});
