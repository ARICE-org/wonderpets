import Constants from "expo-constants";
import { Platform } from "react-native";

const stripTrailingSlash = (value: string) => value.replace(/\/+$/, "");

const getDevHost = (): string | null => {
  const hostUri =
    Constants.expoConfig?.hostUri ??
    // Expo Go
    (Constants as any).expoGoConfig?.debuggerHost ??
    // Older manifests
    (Constants as any).manifest2?.extra?.expoGo?.debuggerHost ??
    (Constants as any).manifest?.debuggerHost ??
    (Constants as any).manifest?.hostUri;

  if (typeof hostUri !== "string" || !hostUri.length) return null;
  return hostUri.split(":")[0];
};

const getWebHost = (): string | null => {
  if (typeof window === "undefined") return null;
  if (!window.location?.hostname) return null;
  return window.location.hostname;
};

export const API_BASE_URL = (() => {
  const devHost = getDevHost();

  const fromEnv = process.env.EXPO_PUBLIC_API_BASE_URL;
  if (typeof fromEnv === "string" && fromEnv.length) {
    const cleaned = stripTrailingSlash(fromEnv);

    // 10.0.2.2 is Android-emulator-only. If we can infer a better host (Expo dev host),
    // prefer that so physical devices + web don't get stuck timing out.
    if (cleaned.includes("10.0.2.2")) {
      if (Platform.OS === "android") {
        if (devHost) return `http://${devHost}:8000`;
        return cleaned;
      }

      // web / ios: ignore emulator-only config
    } else {
      return cleaned;
    }
  }

  if (Platform.OS === "web") {
    const host = getWebHost() ?? "localhost";
    return `http://${host}:8000`;
  }

  if (devHost) {
    return `http://${devHost}:8000`;
  }

  if (Platform.OS === "android") return "http://10.0.2.2:8000";
  return "http://localhost:8000";
})();
