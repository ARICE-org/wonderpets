import React, { useState } from "react";
import {
  VStack,
  HStack,
  Text,
  Button,
  Checkbox,
  CheckboxGroup,
  CheckboxIndicator,
  CheckboxIcon,
  CheckboxLabel,
  CheckIcon,
  Input,
  InputField,
} from "@gluestack-ui/themed";
import { SafeAreaView } from "react-native-safe-area-context";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useRice } from "../../../../context/riceContext";

export default function RiceEntryScreen() {
  const router = useRouter();
  const { riceId, riceName } = useLocalSearchParams();
  const { markAsPlanted } = useRice();

  const [landPrep, setLandPrep] = useState("Oo");
  const [isPlanted, setIsPlanted] = useState("Hindi");

  return (
    <SafeAreaView style={{ flex: 1 }}>
      <VStack p="$4" space="lg">
        <Text fontSize="$xl" fontWeight="$bold">
          {riceName}
        </Text>

        {/* LAND PREPARATION */}
        <VStack space="sm">
          <Text fontWeight="$bold">
            Nagawa mo na ba ang preparation sa lupa?
          </Text>

          <CheckboxGroup
            value={[landPrep]}
            onChange={(values) => setLandPrep(values[0])}
          >
            <HStack space="xl">
              <Checkbox value="Oo">
                <CheckboxIndicator mr="$2">
                  <CheckboxIcon as={CheckIcon} />
                </CheckboxIndicator>
                <CheckboxLabel>Oo</CheckboxLabel>
              </Checkbox>

              <Checkbox value="Hindi">
                <CheckboxIndicator mr="$2">
                  <CheckboxIcon as={CheckIcon} />
                </CheckboxIndicator>
                <CheckboxLabel>Hindi</CheckboxLabel>
              </Checkbox>
            </HStack>
          </CheckboxGroup>
        </VStack>

        {/* PLANTING STATUS */}
        <VStack space="sm">
          <Text fontWeight="$bold">Na itanim mo na ba ang mga punla?</Text>

          <CheckboxGroup
            value={[isPlanted]}
            onChange={(values) => setIsPlanted(values[0])}
          >
            <HStack space="xl">
              <Checkbox value="Oo">
                <CheckboxIndicator mr="$2">
                  <CheckboxIcon as={CheckIcon} />
                </CheckboxIndicator>
                <CheckboxLabel>Oo</CheckboxLabel>
              </Checkbox>

              <Checkbox value="Hindi">
                <CheckboxIndicator mr="$2">
                  <CheckboxIcon as={CheckIcon} />
                </CheckboxIndicator>
                <CheckboxLabel>Hindi</CheckboxLabel>
              </Checkbox>
            </HStack>
          </CheckboxGroup>
        </VStack>

        {/* INPUT */}
        <Input>
          <InputField
            placeholder="Ilang sako ng punla?"
            keyboardType="numeric"
          />
        </Input>

        {/* ACTION BUTTONS */}
        <HStack space="md" mt="$6">
          <Button
            flex={1}
            bg="$emerald600"
            onPress={() => {
              markAsPlanted(riceId as string);
              router.back();
            }}
          >
            <Text color="$white">Confirm</Text>
          </Button>

          <Button flex={1} variant="outline" onPress={() => router.back()}>
            <Text>Cancel</Text>
          </Button>
        </HStack>
      </VStack>
    </SafeAreaView>
  );
}
