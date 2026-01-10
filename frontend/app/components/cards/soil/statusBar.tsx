import React from "react";
import { HStack, Box } from "@gluestack-ui/themed";

const StatusBar = () => (
  <Box px="$2" mt="$4" mb="$2" width="50%">
    <HStack
      height={8}
      overflow="hidden"
      gap="$1"
      width="100%"
    >
      <Box flex={2} bg="$green500" width="100%" />
      <Box flex={2} bg="$orange500" width="100%" />
      <Box flex={2} bg="$red500" width="100%" />
    </HStack>
  </Box>
);

export default StatusBar;
