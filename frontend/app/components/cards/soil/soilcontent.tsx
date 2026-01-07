import React from "react";
import { Box, VStack, HStack, Text, Pressable } from "@gluestack-ui/themed";

export default function AdditionalSoilContent() {
  return (
    <Box bg="$white" p="$4" mb="$4" rounded="$lg">
      <Text fontSize="$lg" fontWeight="bold" mb="$3">
        Additional Soil Content
      </Text>

      <HStack justifyContent="space-around" mb="$4">
        <VStack alignItems="center">
          <Text fontWeight="bold" color="$red600" fontSize="$2xl">
            3 pH
          </Text>
          <Text>Soil pH</Text>
        </VStack>
        <VStack alignItems="center">
          <Text fontWeight="bold" color="$green600" fontSize="$2xl">
            90%
          </Text>
          <Text>Moisture</Text>
        </VStack>
      </HStack>

      <Pressable p="$3" bg="$green100" rounded="$md" alignItems="center">
        <Text color="$green800" fontWeight="bold">
          Possible Actions
        </Text>
      </Pressable>
    </Box>
  );
}
