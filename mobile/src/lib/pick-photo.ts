import * as ImagePicker from 'expo-image-picker';

import type { Photo } from './types';

// Lower quality keeps uploads small and fast; the detector shrinks photos anyway.
const OPTIONS: ImagePicker.ImagePickerOptions = { mediaTypes: 'images', quality: 0.7 };

export type PickResult =
  | { kind: 'picked'; photo: Photo }
  | { kind: 'cancelled' }
  | { kind: 'error'; message: string };

/** Open the camera or the gallery and return the chosen photo. */
export async function pickPhoto(source: 'camera' | 'gallery'): Promise<PickResult> {
  try {
    if (source === 'camera') {
      const permission = await ImagePicker.requestCameraPermissionsAsync();
      if (!permission.granted) {
        return {
          kind: 'error',
          message: 'Camera access is off. Allow it in your phone settings, or choose a photo from the gallery.',
        };
      }
    }
    const picked =
      source === 'camera'
        ? await ImagePicker.launchCameraAsync(OPTIONS)
        : await ImagePicker.launchImageLibraryAsync(OPTIONS);
    if (picked.canceled) {
      return { kind: 'cancelled' };
    }
    const asset = picked.assets[0];
    return {
      kind: 'picked',
      photo: { uri: asset.uri, mimeType: asset.mimeType, fileName: asset.fileName, file: asset.file },
    };
  } catch {
    return {
      kind: 'error',
      message:
        source === 'camera'
          ? 'The camera could not be opened on this device. Choose a photo from the gallery.'
          : 'The gallery could not be opened. Try again.',
    };
  }
}
