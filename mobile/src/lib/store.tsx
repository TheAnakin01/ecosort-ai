import AsyncStorage from '@react-native-async-storage/async-storage';
import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

import { addRecord, parseHistory, removeRecord } from './history';
import { forgetPhoto } from './photo-store';
import type { Photo, ScanRecord } from './types';

const STORAGE_KEY = 'ecosort.history.v1';

type Store = {
  /** False until saved history has been read from the device. */
  loaded: boolean;
  history: ScanRecord[];
  addScan: (record: ScanRecord) => Promise<void>;
  removeScan: (id: string) => Promise<void>;
  clearHistory: () => Promise<void>;
  /** A photo picked on the Home screen, waiting for the Scan screen to show it. */
  pendingPhoto: Photo | null;
  setPendingPhoto: (photo: Photo | null) => void;
};

const StoreContext = createContext<Store | null>(null);

async function save(history: ScanRecord[]): Promise<void> {
  try {
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch (error) {
    // Storage full or unavailable: the scan still shows now, it just will not
    // be there after the app restarts.
    console.warn('Could not save scan history', error);
  }
}

async function forgetPhotos(records: ScanRecord[]): Promise<void> {
  await Promise.all(records.map((record) => forgetPhoto(record.photoUri).catch(() => undefined)));
}

/** Keeps the scan history in memory and on the device. */
export function StoreProvider({ children }: { children: ReactNode }) {
  const [history, setHistory] = useState<ScanRecord[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [pendingPhoto, setPendingPhoto] = useState<Photo | null>(null);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .catch(() => null)
      .then((raw) => {
        // Keep any scan made while the saved history was still loading.
        setHistory((current) => {
          const saved = parseHistory(raw).filter((item) => !current.some((c) => c.id === item.id));
          return [...current, ...saved];
        });
        setLoaded(true);
      });
  }, []);

  async function addScan(record: ScanRecord) {
    const result = addRecord(history, record);
    setHistory(result.history);
    await save(result.history);
    await forgetPhotos(result.removed);
  }

  async function removeScan(id: string) {
    const removed = history.filter((item) => item.id === id);
    const next = removeRecord(history, id);
    setHistory(next);
    await save(next);
    await forgetPhotos(removed);
  }

  async function clearHistory() {
    const removed = history;
    setHistory([]);
    await save([]);
    await forgetPhotos(removed);
  }

  return (
    <StoreContext.Provider
      value={{ loaded, history, addScan, removeScan, clearHistory, pendingPhoto, setPendingPhoto }}>
      {children}
    </StoreContext.Provider>
  );
}

export function useStore(): Store {
  const value = useContext(StoreContext);
  if (!value) {
    throw new Error('useStore must be used inside StoreProvider');
  }
  return value;
}
