import React from "react";
import { Box } from "@gluestack-ui/themed";
import MainScreen from "../(tabs)/(stack)/MainScreen";

export default function HomeScreen() {
  return (
    <Box flex={1} bg="$white">
      <MainScreen />
    </Box>
  );
}
