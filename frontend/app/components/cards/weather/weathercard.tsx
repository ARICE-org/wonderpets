import React from "react";
import { Box, Text, Image } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";

interface WeatherCardProps {
    day: string;
    temperature: string;
    wind: string;
    icon?: any; // optional, can be a require() image or undefined
}

export default function WeatherCard({ day, temperature, wind, icon }: WeatherCardProps) {
    return (
        <BaseCard
            w={110}
            h={160}
            mx="$1"
            p="$3"
            rounded="$lg"
            bg="$coolGray100"
            alignItems="center"
        > <Box
            bg="#00C37D"
            px="$3"
            py="$1"
            rounded="$md"
            mb="$2"
        > <Text fontSize="$sm" fontWeight="$bold" color="$white">
                    {day} </Text> </Box>

            ```
            <Text fontSize="$xl" fontWeight="$bold" color="$black">
                {temperature}
            </Text>

            {/* Render icon only if it exists */}
            {icon && (
                <Image
                    source={icon}
                    alt="weather-icon"
                    w={40}
                    h={40}
                    mt="$1"
                />
            )}

            <Text mt="$1" fontSize="$xs" color="$coolGray600">
                {wind}
            </Text>
        </BaseCard>
    );
}