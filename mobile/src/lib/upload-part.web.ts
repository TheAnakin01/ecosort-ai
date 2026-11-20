import type { Photo } from './types';

/** The photo as a multipart form part, in the browser. */
export async function uploadPart(photo: Photo): Promise<Blob> {
  return photo.file ?? (await (await fetch(photo.uri)).blob());
}
