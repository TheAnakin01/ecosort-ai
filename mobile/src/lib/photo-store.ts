import { Directory, File, Paths } from 'expo-file-system';

// The image picker puts photos in a cache folder that the phone may empty.
// Scans kept in history need their photo copied somewhere permanent.

const folder = new Directory(Paths.document, 'scans');

/** Copy a picked photo into the app's own storage and return the new uri. */
export async function keepPhoto(uri: string, id: string): Promise<string> {
  if (!folder.exists) {
    folder.create({ intermediates: true });
  }
  const extension = uri.match(/\.(\w{3,4})(?:\?|$)/)?.[1] ?? 'jpg';
  const target = new File(folder, `${id}.${extension}`);
  new File(uri).copy(target);
  return target.uri;
}

/** Delete a photo saved by keepPhoto. Missing files are fine. */
export async function forgetPhoto(uri: string): Promise<void> {
  const file = new File(uri);
  if (file.exists) {
    file.delete();
  }
}
