import React from "react";
import { HStack, ScrollView, Text } from "@gluestack-ui/themed";
import RiceCard from "./riceCard";

const riceList = ["RC 222", "RC 160", "RC 480", "Jasmin"];

export default function RiceRecommended() {
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
        <HStack px="$1" py="$3">
          {riceList.map((rice, index) => (
            <RiceCard key={index} label={rice} />
          ))}
        </HStack>
      </ScrollView>
    </>
  );
}
