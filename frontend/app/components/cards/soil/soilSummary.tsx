import React from "react";
import { VStack, HStack, Text } from "@gluestack-ui/themed";
import { TouchableOpacity, Pressable } from "react-native";
import { useSoilForecast } from "../../../../hooks/useSoilForecast";
import { transformForecastToMetrics, fallbackSoilMetrics } from "./soildata";
import MetricRow from "./metricRow";
import StatusBar from "./statusBar";
import { router } from "expo-router";

interface SoilSummaryProps {
  farmerId?: string;
}

export default function SoilSummary({ 
  farmerId = "b4c478ad-ca81-4576-aed1-0a6f828b8602" 
}: SoilSummaryProps) {
  // Fetch real data from API
  const { data: forecast } = useSoilForecast(farmerId);

  // Get metrics from API or use fallback
  const soilMetrics = 
    forecast && forecast.weeklyForecast.length > 0
      ? transformForecastToMetrics(forecast.weeklyForecast[0])
      : fallbackSoilMetrics;

  const row1 = soilMetrics.slice(0, 2);
  const row2 = soilMetrics.slice(2, 4);

  return (
    <VStack>
      <HStack
        justifyContent="space-between"
        alignItems="center"
        mb="$4"
        mx="$2"
      >
        <Text fontSize="$xl" fontWeight="$bold" color="$black">
          Soil Summary
        </Text>
        <Pressable
          onPress={() => router.push("/(tabs)/(stack)/soil/soilScreeen")}
        >
          <Text fontSize="$2xl" fontWeight="$bold" color="$coolGray500">
            →
          </Text>
        </Pressable>
      </HStack>
      <MetricRow metrics={row1} />
      <MetricRow metrics={row2} />
      <StatusBar />
    </VStack>
  );
}
