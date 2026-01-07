import { VStack, Text, Image } from "@gluestack-ui/themed";

interface CurrentWeatherProps {
  temperature: number;
  condition: string;
  icon: any;
}

export default function CurrentWeather({
  temperature,
  condition,
  icon,
}: CurrentWeatherProps) {
  return (
    <VStack alignItems="center" mt="$8">
      <Image source={icon} alt="Weather Icon" size="2xl" />

      <Text fontSize="$5xl" fontWeight="$bold" mt="$4">
        {temperature}°C
      </Text>

      <Text fontSize="$md" color="$coolGray500">
        {condition}
      </Text>
    </VStack>
  );
}
