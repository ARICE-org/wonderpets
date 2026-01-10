import React from "react";
import { VStack, HStack, Text, Box } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import type { WeeklyForecastData } from "../../../../lib/api/services/soil-forecast.types";

interface NutrientRangeCardProps {
  data?: WeeklyForecastData;
}

export default function NutrientRangeCard({ data }: NutrientRangeCardProps) {
  if (!data) return null;

  // Ideal ranges for Rice (generic placeholders, should be moved to a config)
  const ranges = {
    nitrogen: { min: 40, max: 80, label: "Nitrogen (N)", unit: "ppm", color: "$blue500" },
    phosphorus: { min: 15, max: 30, label: "Phosphorus (P)", unit: "ppm", color: "$teal500" },
    potassium: { min: 0.5, max: 1.5, label: "Potassium (K)", unit: "meq/100g", color: "$orange500" },
  };

  const renderMeter = (val: number | undefined, field: keyof typeof ranges) => {
    const current = val ?? 0;
    const info = ranges[field];
    const percentage = Math.min(Math.max((current / (info.max * 1.2)) * 100, 5), 100);

    let statusText = "Optimal";
    let statusColor = "$green600";

    if (current < info.min) {
      statusText = "Deficit";
      statusColor = "$red600";
    } else if (current > info.max) {
      statusText = "Surplus";
      statusColor = "$orange600";
    }

    return (
      <VStack space="xs" key={field} mb="$4">
        <HStack justifyContent="space-between" alignItems="flex-end">
          <VStack>
            <Text fontSize="$xs" color="$textLight500" fontWeight="$medium">{info.label}</Text>
            <Text fontSize="$md" fontWeight="$bold" color={info.color}>
              {current} <Text fontSize="$xs" color="$textLight500">{info.unit}</Text>
            </Text>
          </VStack>
          <Text fontSize="$2xs" color={statusColor} fontWeight="$bold" textTransform="uppercase">
            {statusText}
          </Text>
        </HStack>

        <Box h="$1.5" bg="$backgroundLight100" rounded="$full" overflow="hidden">
          <Box
            h="100%"
            w={`${percentage}%`}
            bg={info.color}
            rounded="$full"
          />
        </Box>

        <HStack justifyContent="space-between">
          <Text fontSize="$2xs" color="$textLight400">Target: {info.min}-{info.max}</Text>
        </HStack>
      </VStack>
    );
  };

  return (
    <BaseCard
      bg="$white"
      mb="$4"
      rounded="$xl"
      p="$5"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 2 }}
      shadowOpacity={0.05}
      shadowRadius={10}
      elevation={3}
    >
      <Text fontSize="$lg" fontWeight="$bold" mb="$4" color="$text900">
        Nutrient Deficit & Surplus
      </Text>

      <VStack space="md">
        {renderMeter(data.nitrogenPpm, 'nitrogen')}
        {renderMeter(data.phosphorusPpm, 'phosphorus')}
        {renderMeter(data.potassiumMeq, 'potassium')}
      </VStack>
    </BaseCard>
  );
}
