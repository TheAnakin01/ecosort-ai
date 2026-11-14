import type { Category, ScanRecord } from './types';

export const MAX_HISTORY = 50;

const CATEGORY_KEYS: Category[] = ['paper', 'plastic', 'metal', 'organic'];

/** Add a scan to the front of the history, dropping the oldest past the limit. */
export function addRecord(history: ScanRecord[], record: ScanRecord): { history: ScanRecord[]; removed: ScanRecord[] } {
  const next = [record, ...history.filter((item) => item.id !== record.id)];
  return { history: next.slice(0, MAX_HISTORY), removed: next.slice(MAX_HISTORY) };
}

export function removeRecord(history: ScanRecord[], id: string): ScanRecord[] {
  return history.filter((item) => item.id !== id);
}

export type HistorySummary = {
  scans: number;
  items: number;
  counts: Record<Category, number>;
  topCategory: Category | null;
};

export function summarize(history: ScanRecord[]): HistorySummary {
  const counts: Record<Category, number> = { paper: 0, plastic: 0, metal: 0, organic: 0 };
  let items = 0;
  for (const record of history) {
    items += record.response.total_objects;
    for (const category of CATEGORY_KEYS) {
      counts[category] += record.response.counts[category] ?? 0;
    }
  }
  let topCategory: Category | null = null;
  for (const category of CATEGORY_KEYS) {
    if (counts[category] > 0 && (topCategory === null || counts[category] > counts[topCategory])) {
      topCategory = category;
    }
  }
  return { scans: history.length, items, counts, topCategory };
}

/** "Just now", "5 min ago", "3 h ago", "Yesterday", then a short date. */
export function formatWhen(iso: string, now: Date = new Date()): string {
  const then = new Date(iso);
  const minutes = Math.floor((now.getTime() - then.getTime()) / 60_000);
  if (Number.isNaN(minutes)) return '';
  if (minutes < 1) return 'Just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  if (hours < 48) return 'Yesterday';
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${then.getDate()} ${months[then.getMonth()]} ${then.getFullYear()}`;
}

/** Read saved history, ignoring anything that is not in the expected shape. */
export function parseHistory(raw: string | null): ScanRecord[] {
  if (!raw) return [];
  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    return [];
  }
  if (!Array.isArray(parsed)) return [];
  return parsed.filter(
    (item): item is ScanRecord =>
      typeof item?.id === 'string' &&
      typeof item?.createdAt === 'string' &&
      typeof item?.photoUri === 'string' &&
      Array.isArray(item?.response?.detections) &&
      typeof item?.response?.counts === 'object' &&
      Array.isArray(item?.guidance),
  );
}
