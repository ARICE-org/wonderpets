import React from "react";
import { VStack, HStack, Text, Pressable, Box } from "@gluestack-ui/themed";
import { useWeeklyForecast } from "../../../../hooks/useSoilForecast";
import { useSoil } from "../../../../context/soilContext";
import { transformForecastToMetrics, fallbackSoilMetrics } from "./soildata";
import MetricRow from "./metricRow";
import StatusBar from "./statusBar";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

interface SoilSummaryProps {
  farmerId?: string;
  isPlanting?: boolean;
}

/**
 * "Get Soil Data" card shown when user is planting but has no soil data
 */
function NoDataCard() {
  const { requestOpenSensorDropdown } = useSoil();

  const handlePress = () => {
    // Set the flag to open sensor dropdown, then navigate to profile
    requestOpenSensorDropdown();
    router.push("/(tabs)/profile");
  };

  return (
    <Pressable onPress={handlePress}>
      <Box
        bg="$blue50"
        borderRadius="$lg"
        p="$4"
        borderWidth={1}
        borderColor="$blue200"
        borderStyle="dashed"
      >
        <HStack space="md" alignItems="center" justifyContent="center">
          <Box
            bg="$blue100"
            p="$3"
            borderRadius="$full"
          >
            <Ionicons name="hardware-chip-outline" size={28} color="#3B82F6" />
          </Box>
          <VStack flex={1}>
            <Text fontSize="$md" fontWeight="$bold" color="$blue800">
              Get Soil Data
            </Text>
            <Text fontSize="$sm" color="$blue600">
              Connect your IoT Sensor to start monitoring soil health
            </Text>
          </VStack>
          <Ionicons name="chevron-forward" size={24} color="#3B82F6" />
        </HStack>
      </Box>
    </Pressable>
  );
}

export default function SoilSummary({
  farmerId = "b4c478ad-ca81-4576-aed1-0a6f828b8602",
  isPlanting = true,
}: SoilSummaryProps) {
  const { setHasSoilData, refreshKey } = useSoil();

  // Use the new weekly forecast specific hook
  const { data: forecast, loading, error, refetch } = useWeeklyForecast(
    farmerId,
    Boolean(isPlanting)
  );

  const hasForecast = Boolean(forecast && forecast.week);

  React.useEffect(() => {
    // Keep context in sync with reality
    if (!isPlanting) {
      setHasSoilData(false);
      return;
    }
    if (!loading) {
      setHasSoilData(hasForecast);
    }
  }, [isPlanting, loading, hasForecast, setHasSoilData]);

  React.useEffect(() => {
    if (!isPlanting) return;
    if (refreshKey > 0) {
      refetch();
    }
  }, [isPlanting, refreshKey, refetch]);

  // Case A: Not planting - hide the card entirely
  if (!isPlanting) {
    return null;
  }

  // Metrics rows (use real data for the single week returned)
  const soilMetrics = hasForecast
    ? transformForecastToMetrics(forecast!)
    : fallbackSoilMetrics;

  return (
    <VStack key={refreshKey}>
      <HStack
        justifyContent="space-between"
        alignItems="center"
        mb="$4"
        mx="$4"
        mt="$6"
      >
        <Text fontSize="$xl" fontWeight="$bold" color="$black">
          Soil Summary
        </Text>
        {hasForecast && (
          <Pressable
            onPress={() => router.push("/(tabs)/(stack)/soil/soilScreen")}
          >
            <Text fontSize="$2xl" fontWeight="$bold" color="$coolGray500">
              →
            </Text>
          </Pressable>
        )}
      </HStack>

      {/* Show loading/metrics/CTA based on result */}
      {loading ? (
        <VStack space="md" alignItems="center" justifyContent="center" py="$4">
          <Text color="$coolGray500">Loading soil data...</Text>
        </VStack>
      ) : hasForecast ? (
        <VStack alignItems="center" px="$4">
          <MetricRow metrics={soilMetrics} />
          <StatusBar />
        </VStack>
      ) : (
        <VStack space="sm">
          <NoDataCard />
          {error && (
            <Text fontSize="$xs" color="$coolGray500" mx="$2">
              {error}
            </Text>
          )}
        </VStack>
      )}
    </VStack>
  );
}
