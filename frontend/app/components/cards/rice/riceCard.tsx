import React from "react";
import {
  VStack,
  Image,
  Text,
  Progress,
  ProgressFilledTrack,
  HStack,
  Badge,
  Pressable,
} from "@gluestack-ui/themed";
import BaseCard from "../baseCard";

interface Props {
  name: string;
  planted: boolean;
  stage?: string;
  progress?: number;
  onPress?: () => void;
}

export default function RiceCard({
  name,
  planted,
  stage,
  progress = 0,
  onPress,
}: Props) {
  return (
    <Pressable onPress={onPress}>
      <BaseCard w={180} h={120} p="$5">
        {!planted ? (
          <VStack flex={1} alignItems="center" justifyContent="center">
            <Image
              source={require("../../../Images/rice.png")}
              alt="Rice"
              size="md"
            />
            <Text mt="$2" fontWeight="$bold">
              {name}
            </Text>
          </VStack>
        ) : (
          <VStack space="xs">
            <HStack justifyContent="space-between" alignItems="center">
              <Text fontWeight="$bold">{name}</Text>
              <Badge bg="$green500">
                <Text color="$white" fontSize="$xs">
                  {stage}
                </Text>
              </Badge>
            </HStack>

            <Text fontSize="$xs" color="$secondary500">
              Planting Progress
            </Text>

            <Progress value={progress} h={6}>
              <ProgressFilledTrack bg="$green500" />
            </Progress>

            <Text fontSize="$xs" textAlign="right">
              {progress}%
            </Text>
          </VStack>
        )}
      </BaseCard>
    </Pressable>
  );
}
