import { Platform } from 'react-native';

import { uploadPart } from './upload-part';
import type { Category, DetectResponse, Guidance, Photo } from './types';

// Set EXPO_PUBLIC_API_URL in mobile/.env. On a real phone "localhost" means
// the phone itself, so use your laptop's Wi-Fi IP address there.
const configuredUrl = process.env.EXPO_PUBLIC_API_URL || '';
export const API_URL = (configuredUrl || 'http://localhost:8000').replace(/\/$/, '');

/**
 * False on the hosted website when no backend address was built in. There the
 * localhost default points at the visitor's own device, where nothing runs.
 */
export function isServerConfigured(): boolean {
  if (configuredUrl) return true;
  if (Platform.OS !== 'web') return true;
  return ['localhost', '127.0.0.1'].includes(globalThis.location?.hostname ?? '');
}

const NOT_CONFIGURED = 'This app is not connected to a server yet, so it cannot scan photos.';

const TIMEOUT_MS = 30_000;

/** An error with a message that is safe to show to the user. */
export class ApiError extends Error {
  /** The backend's error code, such as "UPLOAD_TOO_LARGE", when it sent one. */
  code?: string;
  /** Set when no answer came back at all, so the caller may wake the server and retry. */
  kind?: 'network' | 'timeout';

  constructor(message: string, code?: string, kind?: 'network' | 'timeout') {
    super(message);
    this.code = code;
    this.kind = kind;
  }
}

async function request(path: string, init?: RequestInit, timeoutMs = TIMEOUT_MS): Promise<Response> {
  if (!isServerConfigured()) {
    throw new ApiError(NOT_CONFIGURED);
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal });
  } catch (error) {
    if (controller.signal.aborted) {
      throw new ApiError('The server took too long to answer. Try again.', undefined, 'timeout');
    }
    const detail = error instanceof Error && error.message ? ` (${error.message})` : '';
    throw new ApiError(
      `Could not reach the server at ${API_URL}. Check your internet connection and try again.${detail}`,
      undefined,
      'network',
    );
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    // The backend answers every failure as { success: false, error: { code, message } }.
    const body = await response.json().catch(() => null);
    const message =
      typeof body?.error?.message === 'string'
        ? body.error.message
        : "We couldn't analyze this photo. Check your connection and try again.";
    throw new ApiError(message, typeof body?.error?.code === 'string' ? body.error.code : undefined);
  }
  return response;
}

async function buildUpload(photo: Photo): Promise<FormData> {
  const form = new FormData();
  form.append('file', await uploadPart(photo), photo.fileName ?? 'photo.jpg');
  return form;
}

/** The free server sleeps when idle and can take about a minute to wake. */
const WAKE_TIMEOUT_MS = 90_000;

export async function detectWaste(photo: Photo): Promise<DetectResponse> {
  const send = async () =>
    request('/api/v1/detect', { method: 'POST', body: await buildUpload(photo) });
  let response: Response;
  try {
    response = await send();
  } catch (error) {
    // No answer at all usually means the server was asleep. Wake it with a
    // light request that may wait up to WAKE_TIMEOUT_MS, then try once more.
    if (!(error instanceof ApiError) || !error.kind) throw error;
    await request('/health', undefined, WAKE_TIMEOUT_MS);
    response = await send();
  }
  return response.json();
}

export async function getGuidance(category: Category): Promise<Guidance> {
  const response = await request(`/api/v1/guidance/${category}`);
  return response.json();
}

/** Detect waste in a photo, then fetch sorting tips for each category found. */
export async function scanPhoto(photo: Photo): Promise<{ response: DetectResponse; guidance: Guidance[] }> {
  const response = await detectWaste(photo);
  const found = (Object.keys(response.counts) as Category[]).filter((c) => response.counts[c] > 0);
  const guidance = await Promise.all(found.map(getGuidance));
  return { response, guidance };
}

export type ServerStatus = 'ready' | 'no-model' | 'offline' | 'not-configured';

/** Is the backend reachable, and does it have a trained model loaded? */
export async function checkServer(): Promise<ServerStatus> {
  if (!isServerConfigured()) {
    return 'not-configured';
  }
  try {
    const response = await request('/health', undefined, 5_000);
    const health = await response.json();
    return health.model_loaded ? 'ready' : 'no-model';
  } catch {
    return 'offline';
  }
}
