import React from "react";
import { HStack, ScrollView, Text, Box } from "@gluestack-ui/themed";
import RiceCard from "./riceCard";
import { useRice } from "../../../../context/riceContext";
import { useRouter } from "expo-router";

export default function RiceRecommended() {
  const { riceList } = useRice();
  const router = useRouter();

  return (
    <Box mt="$2">
      <Text px="$4" fontSize="$lg" fontWeight="$bold">
        Recommended Rice
      </Text>

      <ScrollView horizontal showsHorizontalScrollIndicator={false}>
        <HStack px="$4" py="$2" space="sm">
          {riceList.map((rice) => (
            <RiceCard
              key={rice.id}
              name={rice.name}
              planted={rice.planted}
              stage={rice.stage}
              progress={rice.progress}
              onPress={() =>
                !rice.planted &&
                router.push({
                  pathname: "/(tabs)/(stack)/reco/RiceEntryScreen",
                  params: {
                    riceId: rice.id,
                    riceName: rice.name,
                  },
                })
              }
            />
          ))}
        </HStack>
      </ScrollView>
    </Box>
  );
}
