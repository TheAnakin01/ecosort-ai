import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

import { theme } from '@/lib/categories';
import { ScanProvider } from '@/lib/scan-context';

export default function RootLayout() {
  return (
    <ScanProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: theme.background },
          headerTintColor: theme.brand,
          headerTitleStyle: { color: theme.text },
          headerShadowVisible: false,
          contentStyle: { backgroundColor: theme.background },
        }}>
        <Stack.Screen name="index" options={{ title: 'EcoSort AI' }} />
        <Stack.Screen name="scan" options={{ title: 'Scan waste' }} />
        <Stack.Screen name="results" options={{ title: 'Results' }} />
      </Stack>
    </ScanProvider>
  );
}
