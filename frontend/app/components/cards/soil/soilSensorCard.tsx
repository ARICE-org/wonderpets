import React from "react";
import { VStack, HStack, Text, Switch, Image } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import { Pressable } from "react-native";
import { router } from "expo-router";

interface soilSensorCardProps {
  id: string;
  label: string;
  status: "Online" | "Offline" | "Cannot Find Device";
  inUse?: boolean;
  imageSource: any;
}

export default function soilSensorCard({
  id,
  label,
  status,
  inUse = false,
  imageSource,
}: soilSensorCardProps) {
  return (
    <>
      <Pressable
        onPress={() =>
          router.navigate({
            pathname: "/(tabs)/(stack)/soil/sensorScreen",
            params: {
              sensorUuid: id,
              label: label,
              status: status,
            },
          })
        }
      >
        <BaseCard
          mx="$1"
          p="$5"
          w={140}
          h={160}
          alignItems="center"
          justifyContent="space-between"
          bg="$coolGray200"
        >
          <Image
            source={imageSource}
            alt={label}
            w={60}
            h={60}
            resizeMode="contain"
          />
          <VStack alignItems="center">
            <Text fontSize="$sm">{label}</Text>
            <Text
              fontSize="$xs"
              color={
                status === "Online"
                  ? "$green500"
                  : status === "Cannot Find Device"
                    ? "$red500"
                    : "$gray500"
              }
            >
              {status}
            </Text>
            {status === "Online" && (
              <HStack alignItems="center" mt="$1">
                <Switch isChecked={inUse} />
                <Text fontSize="$xs" ml="$2">
                  {inUse ? "In-Use" : "Idle"}
                </Text>
              </HStack>
            )}
          </VStack>
        </BaseCard>
      </Pressable>
    </>
  );
}
