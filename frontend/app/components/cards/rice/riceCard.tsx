import React from "react";
import { Text, VStack, Image, Pressable } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";

interface RiceCardProps {
  label: string;
  onPress: () => void;
}

export default function RiceCard({ label, onPress }: RiceCardProps) {
  return (
    <Pressable
      onPress={() => {
        console.log("Pressed:", label);
        onPress();
      }}
      justifyContent="center"
      alignItems="center"
    >
      <BaseCard mx="$1" p="$0" w={100} h={120}>
        <VStack alignItems="center">
          <Image
            source={require("../../../Images/rice.png")}
            alt="Rice"
            size="md"
          />
          <Text mt="$1" fontSize="$sm" color="$black">
            {label}
          </Text>
        </VStack>
      </BaseCard>
    </Pressable>
  );
}
