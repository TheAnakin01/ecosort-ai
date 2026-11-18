import { File } from 'expo-file-system';

import type { Photo } from './types';

/**
 * The photo as a multipart form part, on Android and iOS.
 *
 * Expo's fetch only accepts parts that can hand over their bytes; React
 * Native's usual { uri, name, type } object fails with "Unsupported
 * FormDataPart implementation". expo-file-system's File provides bytes().
 */
export function uploadPart(photo: Photo): Blob {
  return new File(photo.uri) as unknown as Blob;
}
