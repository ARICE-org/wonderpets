import React from "react";
import { VStack, HStack, Text } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import { data as nutrients } from "./soildata";

export default function suggestednutrients() {
  return (
    <BaseCard
      bg="$white"
      p="$4"
      mb="$6"
      rounded="$lg"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 0 }}
      shadowOpacity={0.2}
      shadowRadius={5}
      elevation={2}
    >
      <Text fontSize="$lg" fontWeight="bold" mb="$3">
        Suggested Nutrients Value
      </Text>
      <VStack space="xs">
        {nutrients.map((item) => (
          <HStack justifyContent="space-between" key={item.label}>
            <Text fontWeight="500">{item.label}</Text>
            <Text color={item.color} fontWeight="600">
              {item.value}
            </Text>
          </HStack>
        ))}
      </VStack>
    </BaseCard>
  );
}
