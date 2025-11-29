import React from "react";
import { Text, VStack } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";

interface RiceCardProps {
  label: string;
}

export default function RiceCard({ label }: RiceCardProps) {
  return (
    <BaseCard mx="$1" p="$3" w={120} h={150} alignItems="center">
      <VStack alignItems="center">
        <Text mt="$2" fontSize="$sm" color="$black">
          {label}
        </Text>
      </VStack>
    </BaseCard>
  );
}
