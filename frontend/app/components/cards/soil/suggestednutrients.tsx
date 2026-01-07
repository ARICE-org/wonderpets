import React from "react";
import { Box, VStack, HStack, Text } from "@gluestack-ui/themed";

interface Nutrient {
  label: string;
  value: string;
  color: string;
}

const nutrients: Nutrient[] = [
  { label: "Nitrogen", value: "27 ppm", color: "#4A90E2" },
  { label: "Phosphorus", value: "30 ppm", color: "#50E3C2" },
  { label: "Potassium", value: "138 ppm", color: "#F5A623" },
  { label: "Calcium", value: "1500 ppm", color: "#7ED321" },
];

export default function suggestednutrients() {
  return (
    <Box
      bg="$white"
      p="$4"
      mb="$4"
      rounded="$lg"
      shadowColor="$black"
      shadowOpacity={0.1}
      shadowRadius={4}
      shadowOffset={{ width: 0, height: 2 }}
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
    </Box>
  );
}
