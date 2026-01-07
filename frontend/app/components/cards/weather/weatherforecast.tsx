import React from "react";
import { HStack, ScrollView, Text } from "@gluestack-ui/themed";
import WeatherCard from "./weathercard";
import { Pressable } from "react-native";
import { router } from "expo-router";

interface ForecastDay {
  day: string;
  temp: string;
  wind: string;
}

interface WeatherForecastProps {
  data: ForecastDay[];
}

export default function WeatherForecast({ data }: WeatherForecastProps) {
  return (
    <>
      <HStack
        px="$4"
        alignItems="center"
        justifyContent="space-between"
        mb="$2"
      >
        <Text fontSize="$lg" fontWeight="$bold" color="$black">
          7 Day Forecast
        </Text>

        <Pressable
          onPress={() =>
            router.navigate("/(tabs)/(stack)/weather/weatherScreen")
          }
        >
          <Text fontSize="$xl" color="$black">
            →
          </Text>
        </Pressable>
      </HStack>

      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <HStack px="$1">
          {data.map((day, index) => (
            <WeatherCard
              key={index}
              day={day.day}
              temperature={day.temp}
              wind={day.wind}
            />
          ))}
        </HStack>
      </ScrollView>
    </>
  );
}
