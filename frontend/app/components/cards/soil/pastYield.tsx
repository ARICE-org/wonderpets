import React from "react";
import { Dimensions, ScrollView } from "react-native";
import { Text, VStack, HStack } from "@gluestack-ui/themed";
import { LineChart } from "react-native-chart-kit";
import BaseCard from "../../../components/cards/baseCard";

const SCREEN_WIDTH = Dimensions.get("window").width;

interface Dataset {
  label: string;
  color: string;
  data: number[];
}

interface Props {
  data: {
    labels: string[];
    datasets: Dataset[];
  };
}

export default function pastYield({ data }: Props) {
  // Make chart wider so it scrolls like NutrientsAnalysis
  const chartWidth = Math.max(SCREEN_WIDTH * 1.5, SCREEN_WIDTH + 500);

  return (
    <BaseCard
      bg="$white"
      rounded="$lg"
      overflow="hidden"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 0 }}
      shadowOpacity={0.2}
      shadowRadius={5}
      elevation={2}
    >
      <VStack space="xs">
        <Text fontWeight="$bold" fontSize="$md">
          Past Yield Data
        </Text>

        {/* ✅ SAME SCROLLABLE CHART PATTERN */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <LineChart
            data={{
              labels: data.labels,
              datasets: data.datasets.map((d) => ({
                data: d.data,
                color: () =>
                  d.color.replace("$", "").startsWith("#")
                    ? d.color
                    : "#66CC66",
                strokeWidth: 1,
              })),
              legend: data.datasets.map((d) => d.label),
            }}
            width={chartWidth}
            height={220}
            bezier
            chartConfig={{
              backgroundGradientFrom: "#fff",
              backgroundGradientTo: "#fff",
              color: () => "#666362",
              labelColor: () => "#100C08",
              propsForDots: {
                r: "4",
                strokeWidth: "2",
                stroke: "#fff",
              },
            }}
            style={{ borderRadius: 12 }}
          />
        </ScrollView>

        {/* Legend (same visual style) */}
        <HStack justifyContent="center" space="md" flexWrap="wrap">
          {data.datasets.map((item, index) => (
            <Text key={index} fontSize="$xs" color={item.color}>
              ● {item.label}
            </Text>
          ))}
        </HStack>
      </VStack>
    </BaseCard>
  );
}
