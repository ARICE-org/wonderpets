import React, { useState, useMemo } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { format, addDays, subDays, isSameDay } from "date-fns";
import { Box, HStack, Pressable, Text } from "@gluestack-ui/themed";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";

const NUM_DAYS_TO_DISPLAY = 7;

interface DateGridItemProps {
  date: Date;
  isActive: boolean;
  isToday: boolean;
}

const DateGridItem = ({ date, isActive, isToday }: DateGridItemProps) => {
  const dayName = format(date, "EEEEE");
  const dayNumber = format(date, "d");

  return (
    <Box
      flex={1}
      alignItems="center"
      justifyContent="center"
      py="$2"
      minWidth={44}
    >
      <Text
        fontSize="$xs"
        fontWeight="$medium"
        color={isActive ? "$black" : "$gray500"}
        mb="$1"
        textTransform="uppercase"
      >
        {isToday ? "TODAY" : dayName}
      </Text>

      <Box
        width={38}
        height={38}
        borderRadius="$full"
        alignItems="center"
        justifyContent="center"
        bg={isActive ? "#34E0A1" : "transparent"} // green highlight
      >
        <Text
          fontSize="$md"
          fontWeight="$bold"
          color={isActive ? "$white" : "$black"}
        >
          {dayNumber}
        </Text>
      </Box>
    </Box>
  );
};

const Header = () => {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const today = new Date();

  // The green highlight initially on today (static for now)
  const [selectedDate] = useState(today);

  const currentMonthYear = format(today, "MMMM yyyy"); // always current month/year

  const datesToDisplay = useMemo(() => {
    const daysBefore = Math.floor(NUM_DAYS_TO_DISPLAY / 2);
    const startDate = subDays(today, daysBefore); // always centered around today
    return Array.from({ length: NUM_DAYS_TO_DISPLAY }, (_, i) =>
      addDays(startDate, i)
    );
  }, [today]);

  // selection state is kept for highlighting, items are not interactive here

  return (
    <SafeAreaView edges={["top"]}>
      <Box bg="$white" mt="$1">
        {/* Top Bar */}
        <Box py="$6" px="$5">
          <HStack justifyContent="space-between" alignItems="center">
            {/* Calendar icon decorative, not clickable */}
            <Pressable
              onPress={() =>
                router.navigate("/(tabs)/(stack)/reco/calendarScreen")
              }
            >
              <Ionicons name="calendar-outline" size={24} color="black" />
            </Pressable>

            {/* Always show current month & year */}
            <Text fontSize="$xl" fontWeight="$bold">
              {currentMonthYear}
            </Text>

            {/* Notification icon (optional) */}
            <Pressable
              onPress={() =>
                router.navigate("/(tabs)/(stack)/notificationScreen")
              }
            >
              <Ionicons name="notifications-outline" size={24} color="black" />
            </Pressable>
          </HStack>
        </Box>

        {/* 7-Day Horizontal Strip */}
        <HStack justifyContent="space-around" px="$2">
          {datesToDisplay.map((date) => (
            <DateGridItem
              key={date.toISOString()}
              date={date}
              isActive={isSameDay(date, selectedDate)}
              isToday={isSameDay(date, today)}
            />
          ))}
        </HStack>
      </Box>
    </SafeAreaView>
  );
};

export default Header;
