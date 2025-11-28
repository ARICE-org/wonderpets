import React from "react";
import { HStack, ScrollView, Text } from "@gluestack-ui/themed";
import WeatherCard from "./weathercard";

const forecastData = [
    { day: "TODAY", temp: "21°C", wind: "12.2 km/h" },
    { day: "TUE", temp: "31°C", wind: "12.0 km/h" },
    { day: "WED", temp: "29°C", wind: "11.5 km/h" },
    { day: "THU", temp: "30°C", wind: "9.3 km/h" },
];

export default function WeatherForecast() {
    return (
        <>
            <HStack px="$4" alignItems="center" justifyContent="space-between" mb="$2">
                <Text fontSize="$lg" fontWeight="$bold" color="$black">
                    7 Day Forecast
                </Text>
                <Text fontSize="$xl" color="$black">→</Text>
            </HStack>

            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                <HStack px="$1">
                    {forecastData.map((day, index) => (
                        <WeatherCard
                            key={index}
                            day={day.day}
                            temperature={day.temp}
                            wind={day.wind}
                        // Do NOT pass icon if you don't have one
                        />
                    ))}
                </HStack>
            </ScrollView>

        </>
    );
}
