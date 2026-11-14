import { Platform } from 'react-native';

import type { Category, DetectResponse, Guidance, Photo, ScanResult } from './types';

// Set EXPO_PUBLIC_API_URL in mobile/.env. On a real phone "localhost" means
// the phone itself, so use your laptop's Wi-Fi IP address there.
export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/$/, '');

const TIMEOUT_MS = 30_000;

/** An error with a message that is safe to show to the user. */
export class ApiError extends Error {}

async function request(path: string, init?: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal });
  } catch {
    throw new ApiError(
      controller.signal.aborted
        ? 'The server took too long to answer. Try again.'
        : `Could not reach the server at ${API_URL}. Check that the backend is running and the phone is on the same Wi-Fi.`,
    );
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    // FastAPI puts the reason in a "detail" field.
    const body = await response.json().catch(() => null);
    const detail = typeof body?.detail === 'string' ? body.detail : `Server error ${response.status}`;
    throw new ApiError(detail);
  }
  return response;
}

async function buildUpload(photo: Photo): Promise<FormData> {
  const form = new FormData();
  if (Platform.OS === 'web') {
    const file = photo.file ?? (await (await fetch(photo.uri)).blob());
    form.append('file', file, photo.fileName ?? 'photo.jpg');
  } else {
    // React Native uploads a local file when given its uri, name and type.
    form.append('file', {
      uri: photo.uri,
      name: photo.fileName ?? 'photo.jpg',
      type: photo.mimeType ?? 'image/jpeg',
    } as unknown as Blob);
  }
  return form;
}

export async function detectWaste(photo: Photo): Promise<DetectResponse> {
  const response = await request('/api/v1/detect', { method: 'POST', body: await buildUpload(photo) });
  return response.json();
}

export async function getGuidance(category: Category): Promise<Guidance> {
  const response = await request(`/api/v1/guidance/${category}`);
  return response.json();
}

/** Detect waste in a photo, then fetch sorting tips for each category found. */
export async function scanPhoto(photo: Photo): Promise<ScanResult> {
  const response = await detectWaste(photo);
  const found = (Object.keys(response.counts) as Category[]).filter((c) => response.counts[c] > 0);
  const guidance = await Promise.all(found.map(getGuidance));
  return { photo, response, guidance };
}
