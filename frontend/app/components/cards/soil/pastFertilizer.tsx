import { Text, VStack, HStack, Box } from "@gluestack-ui/themed";
import BaseCard from "../../../components/cards/baseCard";

const Item = ({ color, label, value }: any) => (
  <HStack justifyContent="space-between" alignItems="center">
    <HStack space="sm" alignItems="center">
      <Box
        w={24}
        h={24}
        borderRadius="$sm"
        bg={color}
        alignItems="center"
        justifyContent="center"
      >
        <Text fontSize="$xs" color="$white" fontWeight="$bold">
          {label[0]}
        </Text>
      </Box>
      <Text>{label}</Text>
    </HStack>
    <Text fontWeight="$bold">{value} ppm</Text>
  </HStack>
);

interface Props {
  data: {
    label: string;
    value: number;
    color: string;
  }[];
}

export default function pastFertilizer({ data }: Props) {
  return (
    <BaseCard w="$full" p="$4" borderRadius="$lg">
      <VStack space="md">
        <Text fontWeight="$bold" fontSize="$md">
          Previous Fertilizer Values
        </Text>
        {data.map((item) => (
          <Text key={item.label}>
            {item.label}: {item.value} ppm
          </Text>
        ))}

        <Item color="$blue500" label="Nitrogen" value={27} />
        <Item color="$green500" label="Phosphorus" value={30} />
        <Item color="$yellow500" label="Potassium" value={138} />
      </VStack>
    </BaseCard>
  );
}
