import React from "react";
import { ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { VStack, HStack, Text, Pressable, Image } from "@gluestack-ui/themed";
import BaseCard from "../../../components/cards/baseCard"; // Adjust the path to your BaseCard
const sensorImage = require("../../../Images/soil_sensor.png"); // Replace with your sensor image

const checklistItems = [
  {
    title: "Turn on the Sensor Device",
    description: "Press the power button located at the top of the device",
  },
  {
    title: "Check the Connectivity",
    description:
      "Check the Bluetooth/Wi-Fi open, press the arrow-head symbol to open",
  },
  {
    title: "Check the Device's distance",
    description:
      "Make sure that the device is within the range of the connection (5 - 8 meters)",
  },
  {
    title: "Reconnect with the system",
    description: "Press the connect button at the top",
  },
];

export default function SensorScreen() {
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
        <VStack space="sm">
          {/* Header Card */}
          <BaseCard p="$4" borderRadius="$md" alignItems="center">
            <Image
              source={sensorImage}
              alt="Sensor Image"
              w={80}
              h={80}
              mb="$2"
            />
            <Text fontSize="$lg" fontWeight="bold">
              Sensor 1
            </Text>
            <Text color="$red600" mb="$2">
              Status: Cannot Find Device
            </Text>
            <HStack space="sm">
              <Pressable
                style={{
                  paddingVertical: 8,
                  paddingHorizontal: 16,
                  backgroundColor: "#555",
                  borderRadius: 8,
                }}
              >
                <Text color="$white">Connect</Text>
              </Pressable>
              <Pressable
                style={{
                  paddingVertical: 8,
                  paddingHorizontal: 16,
                  backgroundColor: "#eee",
                  borderRadius: 8,
                }}
              >
                <Text>⟳</Text>
              </Pressable>
            </HStack>
          </BaseCard>

          {/* Device Connection Checklist */}
          <Text fontSize="$md" fontWeight="bold" mb="$2">
            Device Connection Checklist
          </Text>
          <Text mb="$4">
            Please follow these steps to prepare for the connection of your
            Sensor Device to the System
          </Text>

          {checklistItems.map((item, index) => (
            <BaseCard
              key={index}
              p="$4"
              mb="$2"
              borderRadius="$md"
              borderWidth={1}
              borderColor="$gray200"
            >
              <HStack alignItems="center" space="md">
                {/* Number Circle */}
                <BaseCard
                  w={30}
                  h={30}
                  rounded={15}
                  alignItems="center"
                  justifyContent="center"
                  bg="$blue500"
                >
                  <Text color="$white">{index + 1}</Text>
                </BaseCard>

                <VStack flex={1}>
                  <Text fontWeight="bold">{item.title}</Text>
                  <Text color="$gray600">{item.description}</Text>
                </VStack>

                <Text color="$gray400">In-Progress</Text>
              </HStack>
            </BaseCard>
          ))}
        </VStack>
      </ScrollView>
    </SafeAreaView>
  );
}
