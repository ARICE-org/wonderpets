import React, { useState, useEffect } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  VStack,
  Text,
  Image,
  Pressable,
  ScrollView as GluestackScrollView,
  HStack,
  Box,
  Spinner,
} from "@gluestack-ui/themed";
import { Alert, ScrollView } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useSoil } from "../../context/soilContext";
import { useCsvUpload } from "../../hooks/useCsvUpload";
import { sensorsService, type SoilSensorDevice } from "../../lib/api/services";
import SoilSensorCard from "../components/cards/soil/soilSensorCard";
const sensorImage = require("../Images/soil_sensor.png");

// Sample farmer data - in production from auth context
const FARMER_ID = "b4c478ad-ca81-4576-aed1-0a6f828b8602";
const PLANTING_DATE = new Date().toISOString().split("T")[0]; // Today's date

export default function ProfileScreen() {
  const [isSoilDropdownOpen, setIsSoilDropdownOpen] = useState(false);
  const [selectedSensor, setSelectedSensor] = useState<string | null>(null);
  const [sensors, setSensors] = useState<SoilSensorDevice[]>([]);
  const [isLoadingSensors, setIsLoadingSensors] = useState(false);

  const {
    shouldOpenSensorDropdown,
    clearDropdownRequest,
    setHasSoilData,
    triggerRefresh,
  } = useSoil();

  useEffect(() => {
    let isMounted = true;

    const loadSensors = async () => {
      setIsLoadingSensors(true);
      try {
        const data = await sensorsService.listSoilSensors({ limit: 100 });
        if (!isMounted) return;
        setSensors(data);

        // Pick a sensible default for uploads
        const firstActive = data.find((s) => s.deviceStatus)?.sensorId;
        const fallback = data[0]?.sensorId;
        setSelectedSensor((prev) => prev ?? firstActive ?? fallback ?? null);
      } catch (e) {
        if (!isMounted) return;
        console.warn("Failed to load sensors", e);
      } finally {
        if (isMounted) setIsLoadingSensors(false);
      }
    };

    loadSensors();
    return () => {
      isMounted = false;
    };
  }, []);

  // CSV upload hook
  const {
    isLoading,
    isUploading,
    error,
    rowCount,
    pickParseAndUpload,
    reset,
  } = useCsvUpload({
    farmerId: FARMER_ID,
    sensorId: selectedSensor || sensors[0]?.sensorId || "",
    plantingDate: PLANTING_DATE,
    onSuccess: (result) => {
      // Always mark as updated immediately so Home refetches even if the user
      // navigates back via gestures/hardware back instead of tapping the alert.
      setHasSoilData(true);
      triggerRefresh();

      Alert.alert(
        "Success!",
        `Soil data uploaded successfully. ${result.message}`,
        [
          {
            text: "Go to Home",
            onPress: () => {
              router.replace("/(tabs)/(stack)/MainScreen");
            },
          },
          {
            text: "Stay",
            style: "cancel",
          },
        ]
      );

      // Clear upload UI state for the next upload.
      reset();
    },
    onError: (errorMessage) => {
      Alert.alert("Upload Failed", errorMessage);
    },
  });

  // Auto-open sensor dropdown if requested from SoilSummary card
  useEffect(() => {
    if (shouldOpenSensorDropdown) {
      setIsSoilDropdownOpen(true);
      clearDropdownRequest();
    }
  }, [shouldOpenSensorDropdown, clearDropdownRequest]);

  const handleUploadCsv = async (sensorId: string) => {
    setSelectedSensor(sensorId);
    await pickParseAndUpload(sensorId);
  };

  const sensorCards = sensors.map((s, idx) => {
    const status = s.deviceStatus ? ("Online" as const) : ("Offline" as const);
    return {
      id: s.sensorId,
      label: s.sensorDesc || `Sensor ${idx + 1}`,
      status,
      inUse: selectedSensor === s.sensorId,
      deviceStatus: s.deviceStatus,
    };
  });

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <ScrollView 
        style={{ flex: 1 }} 
        contentContainerStyle={{ paddingBottom: 40 }}
        showsVerticalScrollIndicator={false}
      >
        <VStack
          flex={1}
          alignItems="center"
          bg="$backgroundLight"
          p="$4"
          space="xs"
        >
          <Text fontSize="$4xl" fontWeight="bold" mb={20}>
            Profile
          </Text>

          {/* Profile Image */}
          <Image
            source={require("../Images/farmer.png")}
            w={150}
            h={150}
            borderRadius={100}
            alt="Profile Image"
          />

          {/* Name and Email */}
          <VStack alignItems="center" space="xs">
            <Text fontSize="$xl" fontWeight="bold">
              John Doe
            </Text>
            <Text fontSize="$sm" color="$gray500" mb="$4">
              johndoe43@example.com
            </Text>
          </VStack>

          {/* Edit Profile Button */}
          <Pressable
            bg="$green500"
            px="$6"
            py="$2"
            borderRadius="$md"
            $pressed={{ opacity: 0.7 }}
          >
            <Text color="$white" fontWeight="bold">
              Edit Profile
            </Text>
          </Pressable>

          {/* Menu Options */}
          <VStack w="100%" mt="$6" space="md">
            {["Farming History", "Soil Sensors", "View Historical Data"].map(
              (item, index) => (
                <VStack
                  key={index}
                  space="sm"
                  borderBlockColor="$coolGray400"
                  borderColor="black"
                >
                  <Pressable
                    flexDirection="row"
                    justifyContent="space-between"
                    alignItems="center"
                    p="$3"
                    borderRadius="$md"
                    $pressed={{ bg: "$gray100" }}
                    onPress={() =>
                      item === "Soil Sensors" &&
                      setIsSoilDropdownOpen(!isSoilDropdownOpen)
                    }
                  >
                    <Text fontSize="$md">{item}</Text>
                    <Text fontSize="$md">
                      {item === "Soil Sensors" && isSoilDropdownOpen ? "▼" : "›"}
                    </Text>
                  </Pressable>

                  {item === "Soil Sensors" && isSoilDropdownOpen && (
                    <VStack space="sm" px="$2">
                      {/* Sensor Cards */}
                      <GluestackScrollView
                        horizontal
                        showsHorizontalScrollIndicator={false}
                        mt="$2"
                      >
                        <HStack space="sm">
                          {isLoadingSensors ? (
                            <Box px="$4" py="$4">
                              <HStack space="sm" alignItems="center">
                                <Spinner size="small" />
                                <Text>Loading sensors...</Text>
                              </HStack>
                            </Box>
                          ) : sensorCards.length === 0 ? (
                            <Box px="$4" py="$4">
                              <Text color="$gray500">No sensors found.</Text>
                            </Box>
                          ) : (
                            sensorCards.map((sensor) => (
                            <SoilSensorCard
                              key={sensor.id}
                              label={sensor.label}
                              status={sensor.status}
                              inUse={sensor.inUse}
                              imageSource={sensorImage}
                            />
                            ))
                          )}
                        </HStack>
                      </GluestackScrollView>

                      {/* CSV Upload Section */}
                      <Box
                        bg="$blue50"
                        p="$4"
                        borderRadius="$lg"
                        mt="$4"
                        borderWidth={1}
                        borderColor="$blue200"
                      >
                        <HStack space="sm" alignItems="center" mb="$2">
                          <Ionicons name="document-text-outline" size={20} color="#2563EB" />
                          <Text fontSize="$md" fontWeight="$bold" color="$blue800">
                            Upload Sensor Data (CSV)
                          </Text>
                        </HStack>
                        <Text fontSize="$sm" color="$blue600" mb="$4">
                          Select a sensor and upload your CSV file with soil readings
                        </Text>

                        <VStack space="sm">
                          {sensorCards
                            .filter((s) => s.deviceStatus)
                            .map((sensor) => (
                            <Pressable
                              key={sensor.id}
                              onPress={() => handleUploadCsv(sensor.id)}
                              disabled={isLoading || isUploading || !sensor.id}
                              bg={isLoading || isUploading ? "$gray300" : "$green500"}
                              px="$4"
                              py="$3"
                              borderRadius="$md"
                              flexDirection="row"
                              alignItems="center"
                              justifyContent="center"
                              $pressed={{ opacity: 0.7 }}
                            >
                              {isLoading || isUploading ? (
                                <Spinner size="small" color="$white" mr="$2" />
                              ) : (
                                <Ionicons
                                  name="cloud-upload-outline"
                                  size={20}
                                  color="white"
                                  style={{ marginRight: 8 }}
                                />
                              )}
                              <Text color="$white" fontSize="$md" fontWeight="$semibold">
                                {isUploading
                                  ? "Uploading..."
                                  : isLoading
                                  ? "Processing..."
                                  : `Upload CSV to ${sensor.label}`}
                              </Text>
                            </Pressable>
                            ))}

                          {sensorCards.filter((s) => s.deviceStatus).length === 0 && !isLoadingSensors && (
                            <Box bg="$amber50" p="$3" borderRadius="$md">
                              <Text color="$amber800" fontSize="$sm">
                                No active sensors available. Activate a sensor in the backend or seed at least one with deviceStatus=true.
                              </Text>
                            </Box>
                          )}
                        </VStack>

                        {error && (
                          <Box bg="$red100" p="$2" borderRadius="$sm" mt="$3">
                            <Text color="$red600" fontSize="$sm">
                              Error: {error}
                            </Text>
                          </Box>
                        )}
                      </Box>
                    </VStack>
                  )}
                </VStack>
              )
            )}
          </VStack>
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
