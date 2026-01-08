import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { ScrollView, VStack, Text } from "@gluestack-ui/themed";

import PastYieldCard from "../../../components/cards/soil/pastYield";
import PastDataValueCard from "../../../components/cards/soil/pastDataValue";
import PastFertilizerCard from "../../../components/cards/soil/pastFertilizer";

export default function SoilManageData() {
  const [selectedYear, setSelectedYear] = useState("2023");

  /* ===== DATA ===== */

  const pastYieldData = {
    labels: ["1st Sem", "2nd Sem", "3rd Sem", "4th Sem"],
    datasets: [
      {
        label: "2022 Yield",
        color: "$blue500",
        data: [20, 45, 60, 40],
      },
      {
        label: "2023 Yield",
        color: "$green500",
        data: [30, 55, 50, 65],
      },
      {
        label: "2024 Yield",
        color: "$yellow500",
        data: [40, 60, 55, 70],
      },
    ],
  };

  const soilDataByYear: any = {
    2023: {
      labels: ["Jan", "Feb", "Mar", "Apr", "May"],
      nitrogen: [30, 20, 45, 25, 35],
      phosphorus: [15, 30, 20, 40, 25],
      potassium: [80, 75, 90, 85, 95],
    },
  };

  const fertilizerValues = [
    { label: "Nitrogen", value: 27, color: "$blue500" },
    { label: "Phosphorus", value: 30, color: "$green500" },
    { label: "Potassium", value: 138, color: "$yellow500" },
  ];

  return (
    <SafeAreaView style={{ flex: 1 }} edges={["top"]}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 16,
          paddingTop: 16,
          paddingBottom: 8, // 👈 small, no gap
        }}
      >
        <VStack px="$4" py="$4" space="lg">
          <Text fontSize="$xl" fontWeight="$bold">
            Manage Soil Data
          </Text>

          <PastYieldCard data={pastYieldData} />

          <PastDataValueCard
            year={selectedYear}
            onYearChange={setSelectedYear}
            data={soilDataByYear[selectedYear]}
          />

          <PastFertilizerCard data={fertilizerValues} />
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
