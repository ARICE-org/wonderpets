import React from "react";
import { Image } from "react-native";
import {
  Modal,
  ModalBackdrop,
  ModalContent,
  Text,
  VStack,
  HStack,
  Button,
  ButtonText,
  Pressable,
  Box,
} from "@gluestack-ui/themed";
import BaseCard from "../baseCard";

interface SelectedRiceDialogProps {
  isOpen: boolean;
  riceName: string;
  onConfirm: () => void;
  onClose: () => void;
}

export default function SelectedRiceModal({
  isOpen,
  riceName,
  onConfirm,
  onClose,
}: SelectedRiceDialogProps) {
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <ModalBackdrop />

      <ModalContent bg="transparent" shadowOpacity={0}>
        <BaseCard w={260} alignItems="center">
          <VStack space="md" alignItems="center">
            {/* Title */}
            <Text fontSize="$sm" color="$coolGray500">
              Selected Rice:
            </Text>

            {/* Image Container */}
            <Box bg="$coolGray200" rounded="$lg" p="$4">
              <Image
                source={require("../../../Images/rice.png")}
                style={{ width: 80, height: 80 }}
                resizeMode="contain"
              />
            </Box>

            {/* Rice Name */}
            <Text fontSize="$lg" fontWeight="$bold">
              {riceName}
            </Text>

            {/* See More */}
            <Pressable>
              <Text fontSize="$sm" color="$coolGray600">
                See More Details →
              </Text>
            </Pressable>

            {/* Buttons */}
            <HStack space="sm" mt="$2">
              <Button bg="$green600" px="$6" onPress={onConfirm}>
                <ButtonText color="$white">Confirm</ButtonText>
              </Button>

              <Button bg="$red500" px="$6" onPress={onClose}>
                <ButtonText color="$white">Cancel</ButtonText>
              </Button>
            </HStack>
          </VStack>
        </BaseCard>
      </ModalContent>
    </Modal>
  );
}
