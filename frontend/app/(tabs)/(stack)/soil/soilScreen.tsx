import React from "react";
import { ScrollView } from "react-native";
import { Box, Text, VStack } from "@gluestack-ui/themed";
import { SafeAreaView } from "react-native-safe-area-context";

import SuggestedNutrients from "../../../components/cards/soil/suggestednutrients";
import AdditionalSoilContent from "../../../components/cards/soil/soilcontent";
import NutrientsAnalysis from "../../../components/cards/soil/nutrientanalysis";

export default function SoilHealthScreen() {
  return (
    <Box flex={1} bg="$white" py={16}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <VStack px="$5" space="md">
          <Text fontSize="$2xl" fontWeight="bold">
            Soil Health Diagnosis
          </Text>

          <SuggestedNutrients />
          <AdditionalSoilContent />
          <NutrientsAnalysis />
        </VStack>
      </ScrollView>
    </Box>
  );
}
