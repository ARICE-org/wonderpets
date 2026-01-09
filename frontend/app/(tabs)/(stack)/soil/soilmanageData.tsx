import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, VStack, Text } from "@gluestack-ui/themed";

import PastYieldCard from "../../../components/cards/soil/pastYield";
import PastDataValueCard from "../../../components/cards/soil/pastDataValue";
import PastFertilizerCard from "../../../components/cards/soil/pastFertilizer";
import {
  pastYieldData,
  fertilizerValues,
  soilDataByYear,
} from "../../../Data/soildata";

export default function SoilManageData() {
  // derive available years from soilDataByYear and set a safe default
  type YearKey = keyof typeof soilDataByYear;
  const availableYears = Object.keys(soilDataByYear).sort((a, b) =>
    b.localeCompare(a)
  ) as YearKey[];
  const [selectedYear, setSelectedYear] = useState<YearKey>(
    availableYears.length
      ? availableYears[0]
      : (Object.keys(soilDataByYear)[0] as YearKey)
  );

  // ensure we always pass a valid data object to the child
  const currentData = soilDataByYear[selectedYear] ??
    soilDataByYear[availableYears[0]] ?? { labels: [], datasets: [] };

  return (
    <SafeAreaView style={{ flex: 1 }} edges={["top"]}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 16,
          paddingTop: 16,
          paddingBottom: 8,
          backgroundColor: "#FFFFFF",
          //   paddingTop: 24, // slightly bigger top padding for title
          //   paddingBottom: 24, // space at the bottom
        }}
      >
        <VStack space="md">
          {/* Title */}
          <Text fontSize="$2xl" fontWeight="$bold" mb="$4" textAlign="center">
            Manage Soil Data
          </Text>

          {/* Past Yield Card */}
          <PastYieldCard data={pastYieldData} />

          {/* Past Data Value Card */}
          <PastDataValueCard
            year={selectedYear}
            onYearChange={(y: string) =>
              setSelectedYear(y as keyof typeof soilDataByYear)
            }
            data={currentData}
          />

          {/* Past Fertilizer Card */}
          <PastFertilizerCard data={fertilizerValues} />
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
