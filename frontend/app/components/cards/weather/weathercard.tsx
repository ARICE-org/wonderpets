import React from "react";
import { Box, Text, VStack } from "@gluestack-ui/themed";
import { Ionicons } from "@expo/vector-icons";
import BaseCard from "../baseCard";

interface WeatherCardProps {
  day: string;
  temperature: string;
  wind: string;
  isToday?: boolean;
}

export default function WeatherCard({
  day,
  temperature,
  wind,
  isToday = false,
}: WeatherCardProps) {
  const accent = "#1DB954";
  const textLight = "#666666";
  const iconColor = isToday ? accent : "#9AA4B2";

  return (
    <BaseCard
      w={isToday ? 100 : 80}
      minHeight={128}
      mx="$1"
      my="$2"
      p="$3"
      rounded="$2xl"
      borderWidth={isToday ? 2 : 0}
      borderColor={isToday ? accent : "transparent"}
      bg="$white"
      alignItems="center"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 10 }}
      shadowOpacity={0.1}
      shadowRadius={14}
      elevation={8}
    >
      {/* Day pill */}
      <Box
        px="$3"
        py="$1"
        rounded="$full"
        bg={isToday ? accent : "$coolGray100"}
        alignItems="center"
      >
        <Text
          fontSize="$2xs"
          fontWeight="$bold"
          color={isToday ? "$white" : textLight}
        >
          {day.toUpperCase()}
        </Text>
      </Box>

      {/* Temperature */}
      <Text mt="$3" fontSize="$xl" fontWeight="$bold" color={accent}>
        {temperature}
      </Text>

      {/* 2D icon */}
      <Box mt="$2">
        <Ionicons name="partly-sunny" size={30} color={iconColor} />
      </Box>

      {/* Wind (kept content, styled subtle) */}
      <Text mt="$2" fontSize="$2xs" color={textLight}>
        {wind}
      </Text>
    </BaseCard>
  );
}
