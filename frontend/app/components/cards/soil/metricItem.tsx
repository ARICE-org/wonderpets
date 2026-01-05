import React from "react";
import { HStack, VStack, Text, Center } from "@gluestack-ui/themed";
import { SoilMetric } from "./soildata";

type MetricItemProps = Omit<SoilMetric, "id" | "color">;

const MetricItem = ({ label, value, unit, status }: MetricItemProps) => {
  let icon: string;
  let iconColor: string;

  switch (status) {
    case "good":
      icon = "✓";
      iconColor = "$green600";
      break;
    case "warning":
      icon = "!";
      iconColor = "$orange600";
      break;
    case "bad":
      icon = "X";
      iconColor = "$red600";
      break;
    default:
      icon = "?";
      iconColor = "$coolGray600";
  }

  return (
    <HStack space="sm" alignItems="center" width="50%">
      <Center width={40} height={40} borderRadius="$full" bg={`${iconColor}20`}>
        <Text fontSize="$xl" fontWeight="$bold" color={iconColor}>
          {icon}
        </Text>
      </Center>
      <VStack>
        <HStack alignItems="flex-end">
          <Text fontSize="$xl" fontWeight="$bold" color={iconColor}>
            {value}
          </Text>
          <Text fontSize="$sm" fontWeight="$medium" color={iconColor} mb="$0.5">
            {unit}
          </Text>
        </HStack>
        <Text fontSize="$sm" color="$coolGray600">
          {label}
        </Text>
      </VStack>
    </HStack>
  );
};

export default MetricItem;
