import React, { useState } from "react";
import { HStack, ScrollView, Text } from "@gluestack-ui/themed";
import RiceCard from "./riceCard";
import SelectedRiceModal from "./SelectedRiceModal";

const riceList = ["RC 222", "RC 160", "RC 480", "Jasmin"];

export default function RiceRecommended() {
  const [selectedRice, setSelectedRice] = useState<string | null>(null);

  return (
    <>
      <HStack
        px="$4"
        alignItems="center"
        justifyContent="space-between"
        mb="$2"
      >
        <Text fontSize="$lg" fontWeight="$bold" color="$black">
          Recommended Rice
        </Text>
        <Text fontSize="$xl" color="$black">
          →
        </Text>
      </HStack>

      {/* Horizontal Scrollable Cards */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <HStack px="$1" py="$1">
          {riceList.map((rice, index) => (
            <RiceCard
              key={index}
              label={rice}
              onPress={() => setSelectedRice(rice)}
            />
          ))}
        </HStack>
      </ScrollView>

      {/* Selected Rice Dialog */}
      <SelectedRiceModal
        isOpen={!!selectedRice}
        riceName={selectedRice ?? ""}
        onConfirm={() => {
          console.log("Confirmed rice:", selectedRice);
          setSelectedRice(null);
        }}
        onClose={() => setSelectedRice(null)}
      />
    </>
  );
}
