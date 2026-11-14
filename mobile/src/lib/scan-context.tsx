import { createContext, useContext, useState, type ReactNode } from 'react';

import type { ScanResult } from './types';

type ScanContextValue = {
  result: ScanResult | null;
  setResult: (result: ScanResult | null) => void;
};

const ScanContext = createContext<ScanContextValue | null>(null);

/** Holds the latest scan so the results screen can read what the scan screen produced. */
export function ScanProvider({ children }: { children: ReactNode }) {
  const [result, setResult] = useState<ScanResult | null>(null);
  return <ScanContext.Provider value={{ result, setResult }}>{children}</ScanContext.Provider>;
}

export function useScan(): ScanContextValue {
  const value = useContext(ScanContext);
  if (!value) {
    throw new Error('useScan must be used inside ScanProvider');
  }
  return value;
}
