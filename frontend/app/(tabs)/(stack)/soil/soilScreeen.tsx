import React from "react";
import { ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { VStack, Text } from "@gluestack-ui/themed";

import SoilContent from "../../../components/cards/soil/soilcontent";
import SuggestedNutrients from "../../../components/cards/soil/suggestednutrients";
import NutrientsAnalysis from "../../../components/cards/soil/nutrientanalysis";

export default function SoilScreen() {
  return (
    // ✅ ONLY TOP SAFE AREA
    <SafeAreaView style={{ flex: 1 }} edges={["top"]}>
      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 16,
          paddingTop: 16,
          paddingBottom: 8,
          backgroundColor: "#FFFFFF",
        }}
      >
        <VStack space="xs">
          <Text fontSize="$2xl" fontWeight="bold" mb="$5" textAlign="center">
            Soil Health Diagnosis
          </Text>

          <SoilContent />
          <SuggestedNutrients />
          <NutrientsAnalysis />
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
