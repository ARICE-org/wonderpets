import React from "react";
import { VStack, HStack, Text, Box } from "@gluestack-ui/themed";
import BaseCard from "../baseCard";
import { Ionicons } from "@expo/vector-icons";

interface SoilHealthCardProps {
  score: number;
  category: string;
  ph: number;
  moisture: number;
}

export default function SoilHealthCard({ score, category, ph, moisture }: SoilHealthCardProps) {
  // Determine color based on health category
  const getStatusColor = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'excellent': return '$green600';
      case 'good': return '$green500';
      case 'fair': return '$orange500';
      case 'poor': return '$red600';
      default: return '$textLight500';
    }
  };

  const getPhStatus = (val: number) => {
    if (val < 5.5) return { label: "Highly Acidic", color: "$red600" };
    if (val < 6.0) return { label: "Acidic", color: "$orange500" };
    if (val > 8.0) return { label: "Alkaline", color: "$orange500" };
    return { label: "Optimal", color: "$green600" };
  };

  const phInfo = getPhStatus(ph);
  const getIconColor = (cat: string) => {
    switch (cat.toLowerCase()) {
      case 'excellent': return '#16A34A'; // green600
      case 'good': return '#22C55E';      // green500
      case 'fair': return '#F97316';      // orange500
      case 'poor': return '#DC2626';      // red600
      default: return '#6B7280';          // textLight500
    }
  };

  const statusColor = getStatusColor(category);
  const iconColor = getIconColor(category);

  return (
    <BaseCard
      bg="$white"
      mb="$4"
      rounded="$xl"
      p="$5"
      shadowColor="black"
      shadowOffset={{ width: 0, height: 2 }}
      shadowOpacity={0.05}
      shadowRadius={10}
      elevation={3}
    >
      <HStack justifyContent="space-between" alignItems="center" mb="$4">
        <VStack>
          <Text fontSize="$sm" color="$textLight500" fontWeight="$medium">Overall Health</Text>
          <Text fontSize="$2xl" fontWeight="$bold" color={statusColor}>{category}</Text>
        </VStack>
        <Box bg={statusColor} p="$3" rounded="$full" opacity={0.1}>
          <Ionicons name="leaf" size={24} color={iconColor} />
        </Box>
      </HStack>

      <Box bg="$backgroundLight50" p="$4" rounded="$lg">
        <HStack justifyContent="space-around">
          <VStack alignItems="center">
            <Text fontWeight="$bold" color={phInfo.color} fontSize="$2xl">
              {ph.toFixed(1)}
            </Text>
            <Text fontSize="$xs" color="$textLight500">Soil pH</Text>
            <Text fontSize="$2xs" color={phInfo.color} fontWeight="$bold" mt="$0.5">
              {phInfo.label}
            </Text>
          </VStack>

          <Box width={1} bg="$borderLight200" height="100%" />

          <VStack alignItems="center">
            <Text fontWeight="$bold" color="$blue600" fontSize="$2xl">
              {moisture}%
            </Text>
            <Text fontSize="$xs" color="$textLight500">Moisture</Text>
            <Text fontSize="$2xs" color="$blue600" fontWeight="$bold" mt="$0.5">
              {moisture > 60 ? "Good" : "Low"}
            </Text>
          </VStack>
        </HStack>
      </Box>
    </BaseCard>
  );
}
