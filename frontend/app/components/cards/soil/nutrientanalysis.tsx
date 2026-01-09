import React from "react";
import { HStack, Text, Pressable } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import { LineChart } from "react-native-chart-kit";
import { Dimensions, ScrollView } from "react-native";

const SCREEN_WIDTH = Dimensions.get("window").width;

export default function NutrientsAnalysis() {
  const data = {
    labels: [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sept",
      "Oct",
      "Nov",
      "Dec",
    ],
    datasets: [
      {
        data: [20, 30, 25, 40, 35, 45, 50, 45, 40, 35, 30, 25],
        color: () => "#4A90E2",
        strokeWidth: 2,
      },
      {
        data: [25, 20, 35, 30, 25, 30, 35, 30, 25, 20, 15, 10],
        color: () => "#50E3C2",
        strokeWidth: 2,
      },
      {
        data: [50, 80, 70, 100, 90, 85, 80, 75, 70, 65, 60, 55],
        color: () => "#F5A623",
        strokeWidth: 2,
      },
    ],
    legend: ["Nitrogen", "Phosphorus", "Potassium"],
  };

  // Make chart wider than the screen so it can be scrolled horizontally.
  const chartWidth = Math.max(SCREEN_WIDTH * 1.5, SCREEN_WIDTH + 500);

  return (
    // clip children so rounded corners hide overflowing chart
    <BaseCard
      bg="$white"
      p="$4"
      mb="$4"
      rounded="$lg"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 0 }}
      shadowOpacity={0.2}
      shadowRadius={5}
      elevation={2}
    >
      <HStack justifyContent="space-between" mb="$3">
        <Text fontSize="$lg" fontWeight="bold">
          Nutrients Analysis
        </Text>
        <Pressable>
          <Text color="$green600">Monthly ▼</Text>
        </Pressable>
      </HStack>

      {/* Horizontal scroll wrapper so chart can be panned left/right */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: 0 }}
      >
        <LineChart
          data={data}
          width={chartWidth}
          height={220}
          chartConfig={{
            backgroundGradientFrom: "#fff",
            backgroundGradientTo: "#fff",
            color: (opacity = 1) => `rgba(0,0,0,${opacity})`,
            labelColor: () => "#999",
            propsForDots: { r: "4", strokeWidth: "2", stroke: "#fff" },
          }}
          bezier
          style={{ borderRadius: 12, marginBottom: 0 }}
        />
      </ScrollView>
    </BaseCard>
  );
}
