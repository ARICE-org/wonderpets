import React from "react";
import { HStack, Text, Box, VStack } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import { LineChart } from "react-native-chart-kit";
import { Dimensions } from "react-native";
import type { WeeklyForecastData } from "../../../../lib/api/services/soil-forecast.types";

const SCREEN_WIDTH = Dimensions.get("window").width;

interface NutrientAnalysisCardProps {
  weeklyData: WeeklyForecastData[];
}

export default function NutrientAnalysisCard({ weeklyData }: NutrientAnalysisCardProps) {
  // Take last 5 weeks for the chart
  const recentData = weeklyData.slice(-5);
  const hasData = recentData.length > 0;

  const chartData = {
    labels: hasData ? recentData.map(d => `W${d.week}`) : ["-", "-", "-", "-", "-"],
    datasets: [
      {
        data: hasData ? recentData.map(d => d.healthScore) : [0, 0, 0, 0, 0],
        color: (opacity = 1) => `rgba(16, 185, 129, ${opacity})`, // Green 500
        strokeWidth: 3,
      }
    ],
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
      <VStack space="md">
        <HStack justifyContent="space-between" alignItems="center">
          <Text fontSize="$lg" fontWeight="$bold" color="$text900">
            Health Trend
          </Text>
          <Box bg="$green100" px="$2" py="$1" rounded="$md">
            <Text fontSize="$2xs" color="$green700" fontWeight="$bold">5 WEEK VIEW</Text>
          </Box>
        </HStack>

        <Box alignItems="center" ml="-$6">
          <LineChart
            data={chartData}
            width={SCREEN_WIDTH - 32}
            height={180}
            chartConfig={{
              backgroundColor: "#ffffff",
              backgroundGradientFrom: "#ffffff",
              backgroundGradientTo: "#ffffff",
              decimalPlaces: 0,
              color: (opacity = 1) => `rgba(16, 185, 129, ${opacity})`,
              labelColor: (opacity = 1) => `rgba(107, 114, 128, ${opacity})`,
              style: {
                borderRadius: 16,
              },
              propsForDots: {
                r: "5",
                strokeWidth: "2",
                stroke: "#ffffff",
              },
              fillShadowGradient: "#10B981",
              fillShadowGradientOpacity: 0.1,
            }}
            withInnerLines={true}
            withOuterLines={false}
            withVerticalLines={false}
            bezier
            style={{
              marginVertical: 8,
              borderRadius: 16,
            }}
          />
        </Box>

        <Text fontSize="$xs" color="$textLight500" textAlign="center" italic>
          Overall health score stability over time
        </Text>
      </VStack>
    </BaseCard>
  );
}
