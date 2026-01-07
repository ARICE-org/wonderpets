import React from "react";
import { Box, HStack, Text, Pressable } from "@gluestack-ui/themed";
import { LineChart } from "react-native-chart-kit";
import { Dimensions } from "react-native";

const SCREEN_WIDTH = Dimensions.get("window").width;

export default function NutrientsAnalysis() {
  const data = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May"],
    datasets: [
      { data: [20, 30, 25, 40, 35], color: () => "#4A90E2", strokeWidth: 2 },
      { data: [25, 20, 35, 30, 25], color: () => "#50E3C2", strokeWidth: 2 },
      { data: [50, 80, 70, 100, 90], color: () => "#F5A623", strokeWidth: 2 },
    ],
    legend: ["Nitrogen", "Phosphorus", "Potassium"],
  };

  return (
    <Box bg="$white" p="$4" mb="$4" rounded="$lg">
      <HStack justifyContent="space-between" mb="$3">
        <Text fontSize="$lg" fontWeight="bold">
          Nutrients Analysis
        </Text>
        <Pressable>
          <Text color="$green600">Monthly ▼</Text>
        </Pressable>
      </HStack>

      <LineChart
        data={data}
        width={SCREEN_WIDTH - 32}
        height={220}
        chartConfig={{
          backgroundGradientFrom: "#fff",
          backgroundGradientTo: "#fff",
          color: (opacity = 1) => `rgba(0,0,0,${opacity})`,
          labelColor: () => "#999",
          propsForDots: { r: "4", strokeWidth: "2", stroke: "#fff" },
        }}
        bezier
        style={{ borderRadius: 12 }}
      />
    </Box>
  );
}
