import React, { useState } from "react";
import { Text, VStack, HStack, Box, Pressable } from "@gluestack-ui/themed";
import BaseCard from "../../../components/cards/baseCard";
import { ScrollView, Dimensions } from "react-native";
import { LineChart } from "react-native-chart-kit";
import { soilDataByYear } from "../../../Data/soildata";

const SCREEN_WIDTH = Dimensions.get("window").width;

interface Dataset {
  label: string;
  color: string; // Hex code like "#34E0A1"
  data: number[];
}

interface Props {
  year: string;
  onYearChange: (year: string) => void;
  data: {
    labels: string[];
    datasets: Dataset[];
  };
}

export default function PastDataValue({ data, year, onYearChange }: Props) {
  // Dynamic chart width based on number of labels
  const chartWidth = Math.max(SCREEN_WIDTH * 1.5, SCREEN_WIDTH + 500);

  return (
    <BaseCard
      w="$full"
      p="$4"
      borderRadius="$lg"
      bg="$white"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 0 }}
      shadowOpacity={0.2}
      shadowRadius={5}
      elevation={2}
    >
      <VStack space="md">
        {/* Header: Title + Year Select */}
        <HStack justifyContent="space-between" alignItems="center">
          <Text fontWeight="$bold" fontSize="$xl">
            Past Data Value
          </Text>

          <DropdownYearSelector year={year} onYearChange={onYearChange} />
        </HStack>

        {/* Description */}
        <Text fontSize="$sm" color="$gray500">
          Past data of Nitrogen, Phosphorus, and Potassium Soil Content.
        </Text>

        {/* Scrollable Line Chart with padding */}
        <Box px="$2" pb="$1">
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <LineChart
              data={{
                labels: data.labels,
                datasets: data.datasets.map((d) => ({
                  data: d.data,
                  color: () => d.color,
                  strokeWidth: 2,
                })),
              }}
              width={chartWidth}
              height={160}
              chartConfig={{
                backgroundGradientFrom: "#fff",
                backgroundGradientTo: "#fff",
                color: (opacity = 1) => "#000",
                labelColor: (opacity = 1) => "#000",
                propsForDots: { r: "4", strokeWidth: "2", stroke: "#fff" },
              }}
              bezier
              style={{ borderRadius: 12 }}
            />
          </ScrollView>
        </Box>

        {/* Legend */}
        <HStack justifyContent="center" space="lg" mt="$2" flexWrap="wrap">
          {data.datasets.map((item, index) => (
            <Text
              key={index}
              fontSize="$xs"
              color={item.color}
              fontWeight="$bold"
            >
              ● {item.label}
            </Text>
          ))}
        </HStack>
      </VStack>
    </BaseCard>
  );
}

function DropdownYearSelector({
  year,
  onYearChange,
}: {
  year: string;
  onYearChange: (y: string) => void;
}) {
  const [open, setOpen] = useState(false);
  // derive available years from soilDataByYear keys and sort descending
  const options = Object.keys(soilDataByYear).sort((a, b) =>
    b.localeCompare(a)
  );

  return (
    // relative container so the dropdown can overlay other content
    <Box style={{ position: "relative" }}>
      <Pressable
        px="$3"
        py="$1"
        borderRadius={8}
        borderWidth={1}
        borderColor="$green600"
        onPress={() => setOpen((s) => !s)}
      >
        <HStack alignItems="center" space="sm">
          <Text fontSize="$sm">{`Year ${year} ▼`}</Text>
        </HStack>
      </Pressable>

      {open && (
        <Box
          // absolute positioned overlay — doesn't push other elements
          style={{
            position: "absolute",
            top: 40,
            right: 0,
            zIndex: 9999,
            justifyContent: "center",
            alignItems: "center",
          }}
          bg="$white"
          width={90}
          borderWidth={1}
          borderColor="$green600"
          rounded="$md"
          overflow="hidden"
        >
          {options.map((o) => (
            <Pressable
              key={o}
              px="$3"
              py="$2"
              onPress={() => {
                onYearChange(o);
                setOpen(false);
              }}
            >
              <Text>{o}</Text>
            </Pressable>
          ))}
        </Box>
      )}
    </Box>
  );
}
