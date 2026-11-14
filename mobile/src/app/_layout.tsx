import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

import { StoreProvider } from '@/lib/store';
import { theme } from '@/lib/theme';

export default function RootLayout() {
  return (
    <StoreProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: theme.background },
          headerTintColor: theme.brand,
          headerTitleStyle: { color: theme.text, fontWeight: '700' },
          headerShadowVisible: false,
          contentStyle: { backgroundColor: theme.background },
        }}>
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="scan" options={{ title: 'Scan waste' }} />
        <Stack.Screen name="results" options={{ title: 'Results' }} />
      </Stack>
    </StoreProvider>
  );
}
