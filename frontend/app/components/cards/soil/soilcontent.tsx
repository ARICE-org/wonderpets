import React from "react";
import { VStack, HStack, Text, Pressable } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import { router } from "expo-router";

export default function soilContent() {
  return (
    <BaseCard
      bg="$white"
      mb="$4"
      rounded="$lg"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 0 }}
      shadowOpacity={0.2}
      shadowRadius={5}
      elevation={2}
    >
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

      <Pressable
        onPress={() => router.navigate("/(tabs)/(stack)/soil/soilmanageData")}
        p="$3"
        bg="$green100"
        rounded="$md"
        alignItems="center"
      >
        <Text color="$green800" fontWeight="bold">
          Possible Actions
        </Text>
      </Pressable>
    </BaseCard>
  );
}
