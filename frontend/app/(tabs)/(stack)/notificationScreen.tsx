import React from "react";
import {
  Box,
  Text,
  VStack,
  HStack,
  ScrollView,
  Pressable,
} from "@gluestack-ui/themed";
import { SafeAreaView } from "react-native-safe-area-context";
import { ChevronLeft } from "lucide-react-native";
import NotificationCard from "../../components/cards/notificationCard";
import { router } from "expo-router";

export default function NotificationScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: "white" }}>
      <Box flex={1}>
        {/* Header */}
        <HStack alignItems="center" px="$4" py="$3">
          <Pressable onPress={() => router.navigate("/MainScreen")}>
            <HStack alignItems="center" space="sm">
              <ChevronLeft size={20} color="#16A34A" />
              <Text color="$green600" fontWeight="$medium">
                Back
              </Text>
            </HStack>
          </Pressable>
        </HStack>

        <ScrollView px="$4">
          {/* Today */}
          <Text fontSize="$sm" color="$coolGray500" mb="$2">
            Today
          </Text>

          <VStack space="md">
            <NotificationCard
              type="success"
              title="Crop Growth Update"
              description="Your rice crop is 75% through its growth cycle. Prepare for harvest planning."
            />

            <NotificationCard
              type="warning"
              title="Water Issues"
              description="It has been 2 days since heavy rain. Go to your field and check if water has drained properly!"
            />

            <NotificationCard
              type="warning"
              title="Weather Updated"
              description="Heavy rain may have washed away nutrients. Check your plants for signs of stress!"
            />

            <NotificationCard
              type="success"
              title="Crop Growth Update"
              description="Your rice crop is 75% through its growth cycle. Prepare for harvest planning."
            />
          </VStack>

          {/* Yesterday */}
          <Text fontSize="$sm" color="$coolGray500" mt="$6">
            Yesterday
          </Text>
        </ScrollView>
      </Box>
    </SafeAreaView>
  );
}
