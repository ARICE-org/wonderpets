import React from "react";
import { VStack, HStack, Text } from "@gluestack-ui/themed";
import { TouchableOpacity } from "react-native";
import { soilMetrics } from "./soildata";
import MetricRow from "./metricRow";
import StatusBar from "./statusBar";

export default function SoilSummary() {
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
        <TouchableOpacity onPress={() => console.log("Go to Soil Details")}>
          <Text fontSize="$2xl" fontWeight="$bold" color="$coolGray500">
            →{" "}
          </Text>
        </TouchableOpacity>
      </HStack>
      ```
      <MetricRow metrics={row1} />
      <MetricRow metrics={row2} />
      <StatusBar />
    </VStack>
  );
}
