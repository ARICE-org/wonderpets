import React from "react";
import { ScrollView, ActivityIndicator } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { VStack, Text, Box, Center } from "@gluestack-ui/themed";
import { useLocalSearchParams } from "expo-router";

import SoilHealthCard from "../../../components/cards/soil/SoilHealthCard";
import NutrientRangeCard from "../../../components/cards/soil/NutrientRangeCard";
import NutrientAnalysisCard from "../../../components/cards/soil/NutrientAnalysisCard";
import { useSoilForecast } from "../../../../hooks/useSoilForecast";

const FARMER_ID = "b4c478ad-ca81-4576-aed1-0a6f828b8602"; // Example ID, should come from context/auth

export default function SoilScreen() {
  const params = useLocalSearchParams();
  const farmerId = (params.farmerId as string) || FARMER_ID;

  const { data, loading, error, refetch } = useSoilForecast(farmerId);

  if (loading && !data) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: "#F9FAFB" }}>
        <Center flex={1}>
          <ActivityIndicator size="large" color="#10B981" />
          <Text mt="$4" color="$textLight500">Analysing soil data...</Text>
        </Center>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "#F9FAFB" }} edges={["top"]}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 16,
          paddingTop: 20,
          paddingBottom: 40,
        }}
      >
        <VStack space="lg">
          <Box mb="$4">
            <Text fontSize="$2xl" fontWeight="$bold" textAlign="center" color="$text900">
              Soil Health Diagnosis
            </Text>
            <Text fontSize="$sm" textAlign="center" color="$textLight500" mt="$1">
              Based on your latest sensor readings
            </Text>
          </Box>

          {/* Overall Health Card */}
          <SoilHealthCard
            score={data?.currentHealthScore || 0}
            category={data?.currentHealthCategory || "Fair"}
            ph={data?.weeklyForecast?.[0]?.pH || 7.0}
            moisture={data?.weeklyForecast?.[0]?.soilMoisturePct || 0}
          />

          {/* Nutrient Deficit/Surplus Card */}
          <NutrientRangeCard
            data={data?.weeklyForecast?.[0]}
          />

          {/* Trend Analysis Card */}
          <NutrientAnalysisCard
            weeklyData={data?.weeklyForecast || []}
          />
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
