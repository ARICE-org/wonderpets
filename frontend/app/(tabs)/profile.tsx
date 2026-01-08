import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import {
  VStack,
  Text,
  Image,
  Pressable,
  ScrollView,
  HStack,
} from "@gluestack-ui/themed";
import SoilSensorCard from "../components/cards/soil/soilSensorCard";
const sensorImage = require("../Images/soil_sensor.png"); // Use require to avoid TypeScript module error

export default function ProfileScreen() {
  const [isSoilDropdownOpen, setIsSoilDropdownOpen] = useState(false); // ✅ Now works

  return (
    <SafeAreaView style={{ flex: 1 }}>
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
          source={require("../Images/farmer.png")} // Replace with your image URL
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
                  <Text fontSize="$md">›</Text>
                </Pressable>

                {item === "Soil Sensors" && isSoilDropdownOpen && (
                  <ScrollView
                    horizontal
                    showsHorizontalScrollIndicator={false}
                    mt="$2"
                    px="$1"
                  >
                    <HStack space="sm">
                      <SoilSensorCard
                        label="Sensor 1"
                        status="Cannot Find Device"
                        imageSource={sensorImage}
                      />
                      <SoilSensorCard
                        label="Sensor 2"
                        status="Online"
                        inUse={true}
                        imageSource={sensorImage}
                      />
                      <SoilSensorCard
                        label="Sensor 3"
                        status="Online"
                        inUse={false}
                        imageSource={sensorImage}
                      />
                    </HStack>
                  </ScrollView>
                )}
              </VStack>
            )
          )}
        </VStack>
      </VStack>
    </SafeAreaView>
  );
}
