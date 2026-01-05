import React from "react";
import { Box, Text, VStack, HStack } from "@gluestack-ui/themed";
import { AlertCircle, Info } from "lucide-react-native";
import BaseCard from "./baseCard";

interface NotificationCardProps {
  type: "success" | "warning";
  title: string;
  description: string;
}

export default function NotificationCard({
  type,
  title,
  description,
}: NotificationCardProps) {
  const isSuccess = type === "success";

  return (
    <BaseCard
      bg={isSuccess ? "$green100" : "$red100"}
      borderWidth={1}
      borderColor={isSuccess ? "$green300" : "$red300"}
    >
      <HStack space="md" alignItems="flex-start">
        {/* Icon */}
        <Box mt="$1">
          {isSuccess ? (
            <Info size={20} color="#16A34A" />
          ) : (
            <AlertCircle size={20} color="#DC2626" />
          )}
        </Box>

        {/* Text */}
        <VStack flex={1} space="xs">
          <Text fontWeight="$semibold" color="$coolGray900">
            {title}
          </Text>
          <Text fontSize="$sm" color="$coolGray700">
            {description}
          </Text>
        </VStack>
      </HStack>
    </BaseCard>
  );
}
