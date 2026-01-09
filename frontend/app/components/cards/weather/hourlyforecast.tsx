import React from "react";
import {
  HStack,
  VStack,
  Text,
  Image,
  ScrollView,
  Box,
} from "@gluestack-ui/themed";
import Svg, { Path } from "react-native-svg";
import BaseCard from "../baseCard";

interface ForecastItem {
  time: string;
  temp: number;
  icon: any;
}

interface HourlyForecastProps {
  data: ForecastItem[];
}

export default function HourlyForecast({ data }: HourlyForecastProps) {
  const maxTemp = Math.max(...data.map((d) => d.temp));
  const minTemp = Math.min(...data.map((d) => d.temp));

  const getY = (temp: number) => {
    const range = maxTemp - minTemp || 1;
    return 20 - ((temp - minTemp) / range) * 12;
  };

  const path = data
    .map((item, index) => {
      const x = index * 60;
      const y = getY(item.temp);
      return `${index === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");

  return (
    <BaseCard p="$1" rounded="$xl" bg="$white" mb="$4">
      <VStack>
        <Text fontSize="$md" fontWeight="$bold" mb="$3">
          24-hour forecast
        </Text>

        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <VStack borderRadius="$md" px="$1" py="$2" bg="$coolGray100">
            {/* Temperature Row */}
            <HStack>
              {data.map((item, index) => (
                <Box key={index} width={60} alignItems="center">
                  <Text fontSize="$md" fontWeight="$medium" color="$green600">
                    {item.temp}°
                  </Text>
                </Box>
              ))}
            </HStack>

            {/* Temperature Line */}
            <Svg height={30} width={data.length * 60}>
              <Path d={path} fill="none" stroke="#22C55E" strokeWidth={2} />
            </Svg>

            {/* Icons + Time */}
            <HStack mt="$2" space="xs">
              {data.map((item, index) => (
                <VStack key={index} width={60} alignItems="center">
                  <Image
                    source={item.icon}
                    alt="Forecast Icon"
                    size="xs"
                    my="$1"
                  />
                  <Text fontSize="$xs" color="$green600">
                    {item.time}
                  </Text>
                </VStack>
              ))}
            </HStack>
          </VStack>
        </ScrollView>
      </VStack>
    </BaseCard>
  );
}
