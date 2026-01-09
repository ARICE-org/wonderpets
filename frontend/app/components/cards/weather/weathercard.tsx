import React from "react";
import { Box, Text, Image, VStack } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";

interface WeatherCardProps {
  day: string;
  temperature: string;
  wind: string;
  icon?: any;
  isToday?: boolean;
}

export default function WeatherCard({
  day,
  temperature,
  wind,
  icon,
  isToday = false,
}: WeatherCardProps) {
  return (
    <BaseCard
      w={90}
      h={150}
      mx="$1"
      p="$0"
      rounded="$2xl"
      borderWidth={0.5}
      borderColor={isToday ? "#34E0A1" : "black"}
      bg="$white"
      alignItems="center"
      overflow="hidden"
    >
      {/* Top green header */}
      <Box w="100%" py="$3" bg="#34E0A1" alignItems="center">
        <Text fontSize="$sm" fontWeight="$bold" color="$white">
          {day}
        </Text>
      </Box>

      {/* Content */}
      <VStack flex={1} alignItems="center" justifyContent="center">
        <Text mt="$2" fontSize="$xl" fontWeight="$bold" color="#00C37D">
          {temperature}
        </Text>

        {icon && (
          <Image
            source={icon}
            alt="weather-icon"
            w={45}
            h={45}
            my="$2"
            resizeMode="contain"
          />
        )}
      </VStack>

      {/* Bottom wind text */}
      <Text mb="$2" fontSize="$xs" color="#00C37D">
        {wind}
      </Text>
    </BaseCard>
  );
}
