# Mobile app

The EcoSort AI phone app, built with React Native and Expo (SDK 58).

## Screens

| Screen | File | What it does |
|---|---|---|
| Home | `src/app/(tabs)/index.tsx` | Scan button, server status, your totals, recent scans |
| History | `src/app/(tabs)/history.tsx` | Every saved scan; open, delete one, or clear all |
| Learn | `src/app/(tabs)/learn.tsx` | What belongs in each material and common mistakes |
| Scan | `src/app/scan.tsx` | Take or pick a photo, preview it, send it to the backend |
| Results | `src/app/results.tsx` | Photo with tappable boxes, counts, item list, sorting tips |

Scans are saved on the device only (the last 50). There are no accounts and no cloud database.

## Run it

1. Start the backend first. See [backend/README.md](../backend/README.md). Use `--host 0.0.0.0` so a phone can reach it.
2. Tell the app where the backend is:

   ```
   cd mobile
   cp .env.example .env
   ```

   Edit `.env` and put your laptop's Wi-Fi IP address in `EXPO_PUBLIC_API_URL`. `localhost` only works in the web version, because on a phone it means the phone itself.
3. Install and start:

   ```
   npm install
   npx expo start
   ```

4. Install **Expo Go** on an Android phone and scan the QR code. The phone and laptop must be on the same Wi-Fi. Press `w` to open the web version in a browser.

Restart `npx expo start` after changing `.env`.

## Checks

```
npm run typecheck
npm run lint
npm test
```

## Building an APK

Use EAS Build: `npx eas-cli@latest build -p android --profile preview`. A release APK blocks plain `http://` addresses, so deploy the backend with `https://` first and set `EXPO_PUBLIC_API_URL` to that address.

## Notes

- Styling uses React Native's built-in `StyleSheet`, not NativeWind as the blueprint planned. It needs no extra setup.
- History uses on-device storage, not Supabase as the blueprint planned.
- The home screen shows whether the backend is reachable. Tap that line to check again.
- The app icon and splash screen are still the Expo defaults in `assets/images/`.
- `AGENTS.md` came with the Expo template. It gives AI coding tools the rules for this Expo version.
