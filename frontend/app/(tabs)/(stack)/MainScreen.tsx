import React from "react";
import { Box, VStack, Text, ScrollView } from "@gluestack-ui/themed";
import Header from "../../components/headCalendar"; // Calendar header
import RiceRecommended from "../../components/cards/rice/riceRecommended";
import WeatherForecast from "../../components/cards/weather/weatherforecast";
import SoilSummary from "../../components/cards/soil/soilSummary";
import SoilSummaryCard from "../../components/cards/soil/SoilSummaryCard";
import forecastData from "../../Data/weatherdata";
import { useRice } from "../../../context/riceContext";

export default function MainScreen() {
  const { riceList } = useRice();

  // Check if any rice is planted (isPlanting = true if at least one is planted)
  const isPlanting = riceList.some((rice) => rice.planted);

  return (
    <Box flex={1} bg="$white">
      <Header />
      <ScrollView flex={1} showsVerticalScrollIndicator={false}>
        <VStack space="sm" px="$4" pt="$4">
          {/* Rice Recommendations */}
          <RiceRecommended />
          {/* Weather Forecast */}
          <WeatherForecast />
          {/*Soil*/}
          {/* Soil Summary - conditionally rendered based on planting status */}
          <SoilSummaryCard isPlanting={isPlanting} />
          {/* Main Content */}
          <VStack alignItems="center" justifyContent="center" py="$6">
            <Text fontSize="$2xl" fontWeight="$semibold" color="$black" mb="$2">
              Home Content
            </Text>
            <Text fontSize="$md" color="$coolGray600" textAlign="center">
              Welcome to the Home tab. 🎉
            </Text>
          </VStack>
        </VStack>
      </ScrollView>
    </Box>
  );
}
