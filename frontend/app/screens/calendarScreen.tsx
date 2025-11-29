import React from "react";
import { Box, Text, VStack, HStack, Pressable } from "@gluestack-ui/themed";
import BaseCard from "../components/cards/baseCard";

export default function CalendarScreen() {
  return (
    <Box flex={1} bg="$white" px="$4" py="$6">
      {/* Back */}
      <Pressable mb="$2">
        <Text fontSize="$md" color="$green600">
          Back
        </Text>
      </Pressable>

      {/* Title */}
      <Text fontSize="$2xl" fontWeight="$bold" textAlign="center" mb="$4">
        Farming Calendar
      </Text>

      {/* Calendar Container Using BaseCard */}
      <BaseCard>
        <VStack>
          {/* Month + Year */}
          <HStack justifyContent="space-between" alignItems="center">
            <Pressable>
              <Text fontSize="$xl"></Text>
            </Pressable>

            <HStack alignItems="center">
              <Text fontSize="$lg" fontWeight="$semibold">
                January
              </Text>

              <Box px="$3" py="$1" bg="$green200" rounded="$md">
                <Text fontSize="$md" fontWeight="$bold">
                  2025
                </Text>
              </Box>
            </HStack>

            <Pressable>
              <Text fontSize="$xl"></Text>
            </Pressable>
          </HStack>

          {/* Weekdays */}
          <HStack justifyContent="space-between" px="$1">
            {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].map((d, i) => (
              <Text key={i} fontSize="$sm" color="$coolGray500">
                {d}
              </Text>
            ))}
          </HStack>

          {/* Dates Grid */}
          <VStack>
            {[
              [30, 1, 2, 3, 4, 5, 6],
              [7, 8, 9, 10, 11, 12, 13],
              [14, 15, 16, 17, 18, 19, 20],
              [21, 22, 23, 24, 25, 26, 27],
              [28, 29, 30, 31, 1, 2, 3],
            ].map((row, rowIndex) => (
              <HStack
                key={rowIndex}
                justifyContent="space-between"
                px="$1"
                mb="$2"
              >
                {row.map((day, colIndex) => (
                  <VStack key={colIndex} alignItems="center">
                    <Text
                      fontSize="$md"
                      color={day === 31 ? "$green600" : "$black"}
                      fontWeight={day === 31 ? "$bold" : "$normal"}
                    >
                      {day}
                    </Text>

                    {/* Dot */}
                    <Box bg="red" w={4} h={4} rounded="$full" mt="$1" />
                  </VStack>
                ))}
              </HStack>
            ))}
          </VStack>
        </VStack>
      </BaseCard>

      {/* Tasks Section */}
      <VStack mt="$4">
        <Text>Apply 40kg/ha Urea on June 9, 2025</Text>
        <Text>Start weeding at 7:00 AM instead of 2:00 PM</Text>
        <Text>Spray insecticide on June 2, 2025, 5:30 AM</Text>
      </VStack>
    </Box>
  );
}
