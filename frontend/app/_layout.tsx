import { Slot } from "expo-router";
import { GluestackUIProvider } from "@gluestack-ui/themed";
import { config } from "@gluestack-ui/config";
import { LogBox } from "react-native";
import { RiceProvider } from "../../frontend/context/riceContext";

// 🔕 Silence native driver warning (Expo safe)
LogBox.ignoreLogs(["Animated: `useNativeDriver` is not supported"]);

export default function RootLayout() {
  return (
    <GluestackUIProvider config={config}>
      <RiceProvider>
        <Slot />
      </RiceProvider>
    </GluestackUIProvider>
  );
}
