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
import { ScrollView } from "react-native";
import { router } from "expo-router";
import { useSoil } from "../../context/soilContext";
import { sensorsService, type SoilSensorDevice } from "../../lib/api/services";
import SoilSensorCard from "../components/cards/soil/soilSensorCard";

const sensorImage = require("../Images/soil_sensor.png");

export default function ProfileScreen() {
  const [isSoilDropdownOpen, setIsSoilDropdownOpen] = useState(false);
  const [sensors, setSensors] = useState<SoilSensorDevice[]>([]);
  const [isLoadingSensors, setIsLoadingSensors] = useState(false);

  const {
    shouldOpenSensorDropdown,
    clearDropdownRequest,
  } = useSoil();

  useEffect(() => {
    let isMounted = true;

    const loadSensors = async () => {
      setIsLoadingSensors(true);
      try {
        const data = await sensorsService.listSoilSensors({ limit: 100 });
        if (isMounted) setSensors(data);
      } catch (e) {
        if (isMounted) console.warn("Failed to load sensors", e);
      } finally {
        if (isMounted) setIsLoadingSensors(false);
      }
    };

    loadSensors();
    return () => {
      isMounted = false;
    };
  }, []);

  // Auto-open sensor dropdown if requested from SoilSummary card
  useEffect(() => {
    if (shouldOpenSensorDropdown) {
      setIsSoilDropdownOpen(true);
      clearDropdownRequest();
    }
  }, [shouldOpenSensorDropdown, clearDropdownRequest]);

  const sensorCards = sensors.map((s, idx) => {
    const status = s.deviceStatus ? ("Online" as const) : ("Offline" as const);
    return {
      id: s.sensorId,
      label: s.sensorDesc || `Sensor ${idx + 1}`,
      status,
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
                                id={sensor.id}
                                label={sensor.label}
                                status={sensor.status}
                                imageSource={sensorImage}
                              />
                            ))
                          )}
                        </HStack>
                      </GluestackScrollView>
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
