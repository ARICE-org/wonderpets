import React from "react";
import { HStack, VStack, Text, Box } from "@gluestack-ui/themed";
import { Ionicons } from "@expo/vector-icons";
import { SoilMetric } from "../../../Data/soildata";

type SoilItemProps = Omit<SoilMetric, "id" | "color">;

const statusConfig = {
  good: {
    color: "#22C55E",
    icon: "checkmark" as const,
  },
  warning: {
    color: "#F97316",
    icon: "alert" as const,
  },
  bad: {
    color: "#EF4444",
    icon: "close" as const,
  },
};

const SoilItem = ({ label, value, unit, status }: SoilItemProps) => {
  const config = statusConfig[status] || statusConfig.good;
  const { color, icon } = config;

  return (
    <HStack space="md" alignItems="center" width="48%" mb="$4">
      {/* Circular Badge with Border */}
      <Box
        width={42}
        height={42}
        borderRadius="$full"
        borderWidth={2}
        borderColor={color}
        alignItems="center"
        justifyContent="center"
        bg="$white"
      >
        <Ionicons name={icon} size={22} color={color} />
      </Box>

      {/* Label and Value Stack */}
      <VStack flex={1}>
        <Text
          fontSize={16}
          fontWeight="$bold"
          style={{ color }}
          numberOfLines={1}
        >
          {label}
        </Text>
        <HStack alignItems="baseline" space="xs">
          <Text
            fontSize={14}
            fontWeight="$semibold"
            style={{ color }}
          >
            {value}
          </Text>
          <Text
            fontSize={12}
            fontWeight="$medium"
            style={{ color }}
          >
            {unit}
          </Text>
        </HStack>
      </VStack>
    </HStack>
  );
};

export default SoilItem;
