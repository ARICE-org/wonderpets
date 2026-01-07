import React, { useState } from "react";
import { SafeAreaView } from "react-native-safe-area-context";
import { format, addDays, subDays, isSameDay } from "date-fns";
import { Box, HStack, Text, Pressable } from "@gluestack-ui/themed";
import { Ionicons } from "@expo/vector-icons"; // Assuming you have Ionicons for the icons
import { router } from "expo-router";

const NUM_DAYS_TO_DISPLAY = 7; // We want to display exactly 7 days

/**
 * Renders a single tappable date item in the grid format.
 */
interface DateGridItemProps {
  date: Date;
  isActive: boolean;
  isToday: boolean;
  onSelectDate: (date: Date) => void;
}

const DateGridItem = ({
  date,
  isActive,
  isToday,
  onSelectDate,
}: DateGridItemProps) => {
  // Format "F", "S", "SN" (Sunday), "T", "W", "TH"
  const dayName = format(date, "EEEEE"); // 'EEEEE' gives a single letter day name
  const dayNumber = format(date, "d");

  return (
    <Pressable
      onPress={() => onSelectDate(date)}
      flex={1} // Each item takes equal width
      alignItems="center"
      justifyContent="center"
      py="$2" // Vertical padding
      px="$1" // Horizontal padding to prevent text from touching edges
      minWidth={44} // Ensure minimum width for touchability
      sx={{
        ":active": {
          opacity: 0.7,
        },
      }}
    >
      <Text
        fontSize="$xs"
        fontWeight="$medium"
        color={isActive ? "$black" : "$gray500"} // Active day name color
        mb="$1" // Margin bottom for spacing
        textTransform="uppercase"
      >
        {isToday ? "TODAY" : dayName}
      </Text>
      <Box
        alignItems="center"
        justifyContent="center"
        width={38} // Fixed width for the circle
        height={38} // Fixed height for the circle
        borderRadius="$full" // Makes it a circle
        bg={isActive ? "#34E0A1" : "transparent"} // Green highlight
      >
        <Text
          fontSize="$md"
          fontWeight="$bold"
          color={isActive ? "$white" : "$black"}
        >
          {dayNumber}
        </Text>
      </Box>
    </Pressable>
  );
};

/**
 * The main Header component
 */
const Header = () => {
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const today = new Date();
  const [selectedDate, setSelectedDate] = useState(today);

  // Get the month from the *selected* date
  const currentMonth = format(selectedDate, "MMMM");

  // Generate 7 dates centered around today's date or a selected date
  const datesToDisplay = React.useMemo(() => {
    const dates = [];
    // Determine the start date to have today in the middle
    // If 7 days, we want 3 days before today, today, and 3 days after.
    const daysBefore = Math.floor(NUM_DAYS_TO_DISPLAY / 2);
    const startDate = subDays(today, daysBefore);

    for (let i = 0; i < NUM_DAYS_TO_DISPLAY; i++) {
      dates.push(addDays(startDate, i));
    }
    return dates;
  }, [today]); // Regenerate only if `today` changes

  return (
    <SafeAreaView edges={["top"]}>
      <Box bg="$white" pb="$5">
        {/* Top Bar: Calendar Icon, Month, Notification Icon */}
        <Box py="$6" px="$5">
          <HStack justifyContent="space-between" alignItems="center">
            <Pressable
              onPress={() => router.push("/(tabs)/(stack)/reco/calendarScreen")}
            >
              <Ionicons name="calendar-outline" size={24} color="black" />
            </Pressable>
            <Text fontSize="$xl" fontWeight="$bold" color="$black">
              {currentMonth}
            </Text>
            <Box>
              <Pressable
                onPress={() =>
                  router.push("/(tabs)/(stack)/notificationScreen")
                }
              >
                <Ionicons
                  name="notifications-outline"
                  size={24}
                  color="black"
                />
              </Pressable>

              <Box
                position="absolute"
                top={-2}
                right={-2}
                width={8}
                height={8}
                borderRadius="$full"
                bg="$red500"
              />
            </Box>
          </HStack>
        </Box>

        {/* Bottom Part: 7-Day Horizontal Strip */}
        <HStack justifyContent="space-around" alignItems="flex-start" px="$2">
          {datesToDisplay.map((date) => (
            <DateGridItem
              key={date.toISOString()}
              date={date}
              isActive={isSameDay(date, selectedDate)}
              isToday={isSameDay(date, today)} // Pass isToday prop
              onSelectDate={setSelectedDate}
            />
          ))}
        </HStack>
      </Box>
    </SafeAreaView>
  );
};

export default Header;
