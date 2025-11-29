// app/(tabs)/profile.tsx
import React from "react";
import { Box, Text, VStack } from "@gluestack-ui/themed";
import ProfileAvatar from "../components/profile_ui/avatar";

export default function ProfileScreen() {
  return (
    <Box flex={1} alignItems="center" justifyContent="center" p="$4">
      <VStack space="md" alignItems="center">
        <Text fontSize="$2xl" fontWeight="$semibold">
          User Profile
        </Text>

        <Text fontSize="$2xl" fontWeight="$semibold" mt="$4">
          Profiled
        </Text>

        <Text>This is the Profile tab.</Text>
      </VStack>
    </Box>
  );
}
