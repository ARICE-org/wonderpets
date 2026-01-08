import {
  Text,
  VStack,
  Box,
  HStack,
  Select,
  SelectTrigger,
  SelectInput,
  SelectIcon,
  ChevronDownIcon,
} from "@gluestack-ui/themed";
import BaseCard from "../../../components/cards/baseCard";

interface Props {
  year: string;
  onYearChange: (year: string) => void;
  data: any;
}

export default function pastDataValue({ data, year, onYearChange }: Props) {
  return (
    <BaseCard w="$full" p="$4" borderRadius="$lg">
      <VStack space="xs">
        <HStack justifyContent="space-between" alignItems="center">
          <Text fontWeight="$bold" fontSize="$md">
            Past Data Value
          </Text>

          <Select>
            <SelectTrigger size="sm" variant="outline">
              <SelectInput placeholder="Year 2023" />
              <SelectIcon>
                <ChevronDownIcon />
              </SelectIcon>
            </SelectTrigger>
          </Select>
        </HStack>

        <Text fontSize="$xs" color="$gray500">
          Past data of Nitrogen, Phosphorus, and Potassium Soil Content.
        </Text>

        {/* Chart */}
        <Box h={160} w="$full" mt="$2" />

        {/* Legend */}
        <HStack justifyContent="center" space="lg">
          <Text fontSize="$xs" color="$blue500">
            ● Nitrogen
          </Text>
          <Text fontSize="$xs" color="$green500">
            ● Phosphorus
          </Text>
          <Text fontSize="$xs" color="$yellow500">
            ● Potassium
          </Text>
        </HStack>
      </VStack>
    </BaseCard>
  );
}
