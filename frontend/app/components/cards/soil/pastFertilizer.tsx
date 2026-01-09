import React from "react";
import { Text, VStack, HStack, Box } from "@gluestack-ui/themed";
import BaseCard from "../../../components/cards/baseCard";

interface FertilizerItem {
  label: string;
  value: number;
  color: string; // Hex color or Gluestack color token
}

interface Props {
  data: FertilizerItem[];
}

// Single item component
const Item = ({ color, label, value }: FertilizerItem) => (
  <HStack justifyContent="space-between" alignItems="center" py="$1">
    <HStack space="sm" alignItems="center">
      <Box
        w={24}
        h={24}
        borderRadius="$sm"
        bg={color}
        alignItems="center"
        justifyContent="center"
      >
        <Text fontSize="$xs" color="$white" fontWeight="$bold">
          {label[0].toUpperCase()}
        </Text>
      </Box>
      <Text fontWeight="$semibold">{label}</Text>
    </HStack>
    <Text fontWeight="$bold">{value} ppm</Text>
  </HStack>
);

export default function PastFertilizer({ data }: Props) {
  return (
    <BaseCard
      w="$full"
      p="$4"
      borderRadius="$lg"
      bg="$white"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 0 }}
      shadowOpacity={0.2}
      shadowRadius={5}
      elevation={2}
    >
      <VStack space="md">
        <Text fontWeight="$bold" fontSize="$md">
          Previous Fertilizer Values
        </Text>

        {/* Map dynamic data */}
        {data.map((item) => (
          <Item
            key={item.label}
            color={item.color}
            label={item.label}
            value={item.value}
          />
        ))}
      </VStack>
    </BaseCard>
  );
}
