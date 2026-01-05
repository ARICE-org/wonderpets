import React from "react";
import { HStack, Box } from "@gluestack-ui/themed";

const StatusBar = () => (
  <HStack
    height={10}
    mx="$10"
    mt="$4"
    borderRadius="$sm"
    overflow="hidden"
    gap="$1"
  >
    <Box flex={1} bg="$green500" borderRadius="$sm" />
    {/* Good */}
    <Box flex={1} bg="$orange500" borderRadius="$sm" />
    {/* Warning */}
    <Box flex={1} bg="$red500" borderRadius="$sm" />

    {/* Bad */}
  </HStack>
);

export default StatusBar;
