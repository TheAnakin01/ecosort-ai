import { Image } from 'expo-image';
import * as ImagePicker from 'expo-image-picker';
import { router } from 'expo-router';
import { useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';

import { Button } from '@/components/button';
import { ApiError, scanPhoto } from '@/lib/api';
import { theme } from '@/lib/categories';
import { useScan } from '@/lib/scan-context';
import type { Photo } from '@/lib/types';

// Lower quality keeps uploads small and fast; the detector resizes to 640px anyway.
const PICKER_OPTIONS: ImagePicker.ImagePickerOptions = { mediaTypes: 'images', quality: 0.7 };

export default function ScanScreen() {
  const { setResult } = useScan();
  const [photo, setPhoto] = useState<Photo | null>(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function pick(source: 'camera' | 'gallery') {
    setError(null);
    if (source === 'camera') {
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      if (!permission.granted) {
        setError('Camera access is off. Allow it in your phone settings, or pick a photo from the gallery.');
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
  }

  async function scan() {
    if (!photo) return;
    setError(null);
    setScanning(true);
    try {
      setResult(await scanPhoto(photo));
      router.push('/results');
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : 'Something went wrong. Try again.');
    } finally {
      setScanning(false);
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      {photo ? (
        <Image source={{ uri: photo.uri }} style={styles.preview} contentFit="contain" accessibilityLabel="Selected photo" />
      ) : (
        <View style={[styles.preview, styles.placeholder]}>
          <Text style={styles.placeholderTitle}>No photo yet</Text>
          <Text style={styles.placeholderBody}>
            Spread the items out, use good light and keep the whole pile in the frame.
          </Text>
        </View>
      )}

      {error ? (
        <View style={styles.error} accessibilityRole="alert">
          <Text style={styles.errorText}>{error}</Text>
        </View>
      ) : null}

      {photo ? <Button label={scanning ? 'Scanning' : 'Scan this photo'} onPress={scan} loading={scanning} /> : null}
      <Button
        label={photo ? 'Retake photo' : 'Take a photo'}
        variant={photo ? 'secondary' : 'primary'}
        onPress={() => pick('camera')}
        disabled={scanning}
      />
      <Button label="Choose from gallery" variant="secondary" onPress={() => pick('gallery')} disabled={scanning} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, gap: 12 },
  preview: { width: '100%', aspectRatio: 1, borderRadius: 16, backgroundColor: theme.card },
  placeholder: {
    borderWidth: 1,
    borderColor: theme.border,
    borderStyle: 'dashed',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
    gap: 8,
  },
  placeholderTitle: { fontSize: 18, fontWeight: '600', color: theme.text },
  placeholderBody: { fontSize: 15, lineHeight: 22, color: theme.muted, textAlign: 'center' },
  error: { backgroundColor: theme.dangerSoft, borderRadius: 12, padding: 14 },
  errorText: { color: theme.danger, fontSize: 15, lineHeight: 21 },
});
