import { VStack, Text } from "@gluestack-ui/themed";

interface LocationLabelProps {
  city: string;
  date: string;
}

export default function locationlabel({ city, date }: LocationLabelProps) {
  return (
    <VStack alignItems="center" mt="$6">
      <Text fontSize="$2xl" fontWeight="$bold">
        {city}
      </Text>
      <Text fontSize="$sm" color="$coolGray500">
        {date}
      </Text>
    </VStack>
  );
}
