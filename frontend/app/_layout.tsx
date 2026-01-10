import React from "react";
import { Slot } from "expo-router";
import { GluestackUIProvider, useToast } from "@gluestack-ui/themed";
import { config } from "@gluestack-ui/config";
import { OverlayProvider } from "@gluestack-ui/core/overlay/creator";
import { ToastProvider } from "@gluestack-ui/core/toast/creator";
import "../global.css";
import { LogBox } from "react-native";
import { RiceProvider } from "../../frontend/context/riceContext";
import { SoilProvider } from "../../frontend/context/soilContext";
import { toastService } from "../lib/services/toast.service";

// 🔕 Silence native driver warning (Expo safe)
LogBox.ignoreLogs(["Animated: `useNativeDriver` is not supported"]);

/**
 * Helper component to initialize the global toast service with the useToast hook
 */
function ToastManager() {
  const toast = useToast();
  React.useEffect(() => {
    toastService.setInstance(toast);
  }, [toast]);
  return null;
}

export default function RootLayout() {
  return (
    <GluestackUIProvider config={config}>
      <OverlayProvider>
        <ToastProvider>
          <ToastManager />
          <RiceProvider>
            <SoilProvider>
              <Slot />
            </SoilProvider>
          </RiceProvider>
        </ToastProvider>
      </OverlayProvider>
    </GluestackUIProvider>
  );
}
