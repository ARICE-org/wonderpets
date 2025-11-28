import React from "react";
import { HStack, Box } from "@gluestack-ui/themed";

const StatusBar = () => (
  <HStack
    height={10}
    mx="$2"
    mt="$4"
    borderRadius="$sm"
    overflow="hidden"
    space="sm"
  >
    <Box flex={1} bg="$green500" borderRadius="$sm" />
    {/* Good */}
    <Box flex={0.5} bg="$orange500" borderRadius="$sm" />
    {/* Warning */}
    <Box flex={0.5} bg="$red500" borderRadius="$sm" />
    {/* Bad */}{" "}
  </HStack>
);

export default StatusBar;
