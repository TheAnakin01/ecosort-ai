// Web version of photo-store.ts. A browser has no app folder to copy into,
// so the photo is shrunk and stored as a data URL that fits in browser storage.

const MAX_SIDE = 900;

export async function keepPhoto(uri: string, _id: string): Promise<string> {
  const image = new Image();
  image.src = uri;
  await image.decode();

  const scale = Math.min(1, MAX_SIDE / Math.max(image.naturalWidth, image.naturalHeight));
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(image.naturalWidth * scale);
  canvas.height = Math.round(image.naturalHeight * scale);
  const context = canvas.getContext('2d');
  if (!context) {
    return uri;
  }
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL('image/jpeg', 0.7);
}

export async function forgetPhoto(_uri: string): Promise<void> {
  // The data URL lives inside the history entry, so there is no file to delete.
}
