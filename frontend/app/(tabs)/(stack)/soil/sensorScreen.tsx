import React from "react";
import { ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { VStack, HStack, Text, Pressable, Image, Box, Spinner } from "@gluestack-ui/themed";
import { Ionicons } from "@expo/vector-icons";
import { router, useLocalSearchParams } from "expo-router";
import { useCsvUpload } from "../../../../hooks/useCsvUpload";
import { useSoil } from "../../../../context/soilContext";
import BaseCard from "../../../components/cards/baseCard";
import { toastService } from "../../../../lib/services/toast.service";

const sensorImage = require("../../../Images/soil_sensor.png");

// Constants (ideally from auth/context)
const FARMER_ID = "b4c478ad-ca81-4576-aed1-0a6f828b8602";
const PLANTING_DATE = new Date().toISOString().split("T")[0];

const checklistItems = [
  {
    title: "Turn on the Sensor Device",
    description: "Press the power button located at the top of the device",
  },
  {
    title: "Check the Connectivity",
    description: "Check the Bluetooth/Wi-Fi open, press the arrow-head symbol to open",
  },
  {
    title: "Check the Device's distance",
    description: "Make sure that the device is within the range of the connection (5 - 8 meters)",
  },
  {
    title: "Reconnect with the system",
    description: "Press the connect button at the top",
  },
];

export default function SensorScreen() {
  const { sensorUuid, label, status } = useLocalSearchParams<{
    sensorUuid: string;
    label: string;
    status: string;
  }>();

  const { setHasSoilData, triggerRefresh } = useSoil();

  // CSV upload hook
  const {
    isLoading,
    isUploading,
    error,
    pickParseAndUpload,
    reset,
  } = useCsvUpload({
    farmerId: FARMER_ID,
    sensorId: sensorUuid || "",
    plantingDate: PLANTING_DATE,
    onSuccess: (result) => {
      console.log("CSV Upload Success:", result);
      setHasSoilData(true);
      triggerRefresh();
      reset();
    },
    onError: (errorMessage) => {
      console.error("CSV Upload Error:", errorMessage);
    },
  });

  const handleUploadCsv = async () => {
    if (!sensorUuid) {
      toastService.showError("No sensor UUID provided.");
      return;
    }
    await pickParseAndUpload();
  };

  return (
    <SafeAreaView style={{ flex: 1 }} edges={["top"]}>
      {/* Custom Header with Back Button */}
      <HStack alignItems="center" px="$4" py="$3" bg="$white" borderBottomWidth={1} borderBottomColor="$gray100">
        <Pressable onPress={() => router.back()} p="$2">
          <Ionicons name="arrow-back" size={24} color="black" />
        </Pressable>
        <Text fontSize="$xl" fontWeight="bold" ml="$2">
          {label || "Sensor Details"}
        </Text>
      </HStack>

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{
          paddingHorizontal: 16,
          paddingTop: 16,
          paddingBottom: 40,
        }}
      >
        <VStack space="md">
          {/* Header Card (Information) */}
          <BaseCard p="$5" borderRadius="$lg" alignItems="center" bg="$white" elevation={1}>
            <Image
              source={sensorImage}
              alt="Sensor Image"
              w={100}
              h={100}
              mb="$3"
              resizeMode="contain"
            />
            <Text fontSize="$2xl" fontWeight="bold" color="$coolGray800">
              {label || "Sensor"}
            </Text>
            <HStack alignItems="center" space="xs" mb="$4">
              <Box
                w={10} h={10} borderRadius={5}
                bg={status === "Online" ? "$green500" : "$red500"}
              />
              <Text fontSize="$md" color={status === "Online" ? "$green600" : "$red600"} fontWeight="$semibold">
                {status || "Disconnected"}
              </Text>
            </HStack>

            <HStack space="md">
              <Pressable
                style={{
                  paddingVertical: 10,
                  paddingHorizontal: 24,
                  backgroundColor: status === "Online" ? "#4ADE80" : "#555",
                  borderRadius: 12,
                }}
              >
                <Text color="$white" fontWeight="$bold">Connect</Text>
              </Pressable>
              <Pressable
                style={{
                  paddingVertical: 10,
                  paddingHorizontal: 16,
                  backgroundColor: "#F3F4F6",
                  borderRadius: 12,
                }}
              >
                <Ionicons name="refresh" size={20} color="#374151" />
              </Pressable>
            </HStack>
          </BaseCard>

          {/* Upload Section */}
          <Text fontSize="$lg" fontWeight="bold" mt="$4" color="$coolGray800">
            Data Inventory
          </Text>
          <Box
            bg="$blue50"
            p="$5"
            borderRadius="$xl"
            borderWidth={1}
            borderColor="$blue200"
          >
            <HStack space="md" alignItems="center" mb="$2">
              <Box bg="$blue100" p="$2" borderRadius="$md">
                <Ionicons name="cloud-upload" size={22} color="#2563EB" />
              </Box>
              <VStack>
                <Text fontSize="$lg" fontWeight="$bold" color="$blue900">
                  Import CSV Data
                </Text>
                <Text fontSize="$xs" color="$blue600">
                  Upload historical soil readings
                </Text>
              </VStack>
            </HStack>

            <Text fontSize="$sm" color="$blue800" mb="$5" lineHeight="$md">
              Manually import soil data from this sensor by selecting a CSV file containing N, P, K, and pH readings.
            </Text>

            <Pressable
              onPress={handleUploadCsv}
              disabled={isLoading || isUploading}
              bg={isLoading || isUploading ? "$gray300" : "$blue600"}
              px="$6"
              py="$3.5"
              borderRadius="$xl"
              flexDirection="row"
              alignItems="center"
              justifyContent="center"
              $pressed={{ opacity: 0.8 }}
            >
              {isLoading || isUploading ? (
                <Spinner size="small" color="$white" mr="$3" />
              ) : (
                <Ionicons name="document-attach" size={20} color="white" style={{ marginRight: 10 }} />
              )}
              <Text color="$white" fontSize="$md" fontWeight="$bold">
                {isUploading ? "Uploading Data..." : isLoading ? "Processing..." : "Choose File & Upload"}
              </Text>
            </Pressable>

            {error && (
              <Box bg="$red50" p="$3" borderRadius="$md" mt="$4" borderWidth={1} borderColor="$red100">
                <HStack space="xs" alignItems="center">
                  <Ionicons name="alert-circle" size={16} color="#DC2626" />
                  <Text color="$red700" fontSize="$xs" flex={1}>
                    Error: {error}
                  </Text>
                </HStack>
              </Box>
            )}
          </Box>

          {/* Device Connection Checklist */}
          <Text fontSize="$lg" fontWeight="bold" mt="$4" color="$coolGray800">
            Troubleshooting
          </Text>
          <Text color="$coolGray500" mb="$2">
            Follow these steps if you are having trouble connecting.
          </Text>

          {checklistItems.map((item, index) => (
            <Box
              key={index}
              p="$4"
              mb="$2"
              bg="$white"
              borderRadius="$lg"
              borderWidth={1}
              borderColor="$coolGray100"
              elevation={1}
            >
              <HStack alignItems="center" space="md">
                <Box
                  w={32}
                  h={32}
                  borderRadius={16}
                  alignItems="center"
                  justifyContent="center"
                  bg="$blue600"
                >
                  <Text color="$white" fontWeight="$bold">{index + 1}</Text>
                </Box>

                <VStack flex={1}>
                  <Text fontWeight="bold" color="$coolGray800">{item.title}</Text>
                  <Text fontSize="$sm" color="$coolGray500">{item.description}</Text>
                </VStack>

                <Ionicons name="chevron-forward" size={18} color="#9CA3AF" />
              </HStack>
            </Box>
          ))}
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
