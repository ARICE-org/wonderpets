import React, { useState } from "react";
import {
  Box,
  Text,
  VStack,
  HStack,
  Pressable,
  ScrollView,
} from "@gluestack-ui/themed";
import BaseCard from "../../../components/cards/baseCard";
import { router } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

const WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// Sample farming tasks
const FARMING_TASKS: Record<string, string[]> = {
  "2026-01-01": ["Apply 40kg/ha Urea", "Irrigate field at 6:00 AM"],
  "2026-01-03": [
    "Start weeding at 7:00 AM",
    "Inspect for pests",
    "Apply fertilizer",
  ],
  "2026-01-05": ["Check pest traps"],
  "2026-01-09": ["Spray insecticide (Imidacloprid) at 5:30 AM"],
  "2026-01-12": ["Fertilize seedlings"],
  "2026-01-15": ["Monitor water levels"],
  "2026-01-20": ["Harvest mature areas"],
  "2026-01-31": ["Check irrigation channels"],
};

export default function CalendarScreen() {
  const today = new Date();
  const [currentDate, setCurrentDate] = useState(
    new Date(today.getFullYear(), today.getMonth(), 1)
  );
  const [selectedDate, setSelectedDate] = useState<string | null>(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDay = new Date(year, month, 1).getDay(); // Sunday=0
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const daysInPrevMonth = new Date(year, month, 0).getDate();
  const adjustedFirstDay = firstDay === 0 ? 6 : firstDay - 1; // make Mon=0

  const calendarDays: {
    day: number;
    isCurrentMonth: boolean;
    fullDate: string;
  }[] = [];

  // previous month filler
  for (let i = adjustedFirstDay - 1; i >= 0; i--) {
    const day = daysInPrevMonth - i;
    calendarDays.push({ day, isCurrentMonth: false, fullDate: "" });
  }

  // current month
  for (let day = 1; day <= daysInMonth; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(
      day
    ).padStart(2, "0")}`;
    calendarDays.push({ day, isCurrentMonth: true, fullDate: dateStr });
  }

  // next month filler
  while (calendarDays.length % 7 !== 0) {
    calendarDays.push({
      day: calendarDays.length - daysInMonth - adjustedFirstDay + 1,
      isCurrentMonth: false,
      fullDate: "",
    });
  }

  const isToday = (item: {
    day: number;
    isCurrentMonth: boolean;
    fullDate: string;
  }) => {
    return (
      item.isCurrentMonth &&
      item.fullDate ===
        `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(
          2,
          "0"
        )}-${String(today.getDate()).padStart(2, "0")}`
    );
  };

  const goToPrevMonth = () => setCurrentDate(new Date(year, month - 1, 1));
  const goToNextMonth = () => setCurrentDate(new Date(year, month + 1, 1));

  return (
    <SafeAreaView
      style={{
        flex: 1,
        backgroundColor: "#ffffff",
        paddingHorizontal: 16,
        paddingVertical: 16,
      }}
    >
      {/* Back Button */}
      <Pressable mb="$4" onPress={() => router.navigate("/MainScreen")}>
        <Text color="$green600" fontSize="$lg">
          ‹ Back
        </Text>
      </Pressable>

      {/* Title */}
      <Text fontSize="$2xl" fontWeight="$bold" textAlign="center" mb="$5">
        Farming Calendar
      </Text>

      {/* Calendar */}
      <BaseCard rounded="$2xl" p="$2">
        <VStack space="md">
          {/* Month Header */}
          <HStack justifyContent="space-between" alignItems="center">
            <Pressable onPress={goToPrevMonth}>
              <Text fontSize="$3xl" color="$green600" ml="$2">
                ‹
              </Text>
            </Pressable>

            <HStack alignItems="center">
              <Text fontSize="$lg" fontWeight="$semibold">
                {currentDate.toLocaleString("default", { month: "long" })}
              </Text>
              <Box bg="$green200" px="$3" py="$1" rounded="$full">
                <Text fontWeight="$bold">{year}</Text>
              </Box>
            </HStack>

            <Pressable onPress={goToNextMonth}>
              <Text fontSize="$3xl" color="$green600" mr="$2">
                ›
              </Text>
            </Pressable>
          </HStack>

          {/* Weekdays */}
          <HStack justifyContent="space-between">
            {WEEK_DAYS.map((d) => (
              <Text
                key={d}
                fontSize="$md"
                color="$black"
                fontWeight="$semibold"
              >
                {d}
              </Text>
            ))}
          </HStack>

          {/* Dates */}
          <VStack>
            {Array.from({ length: calendarDays.length / 7 }).map(
              (_, rowIndex) => (
                <HStack key={rowIndex} justifyContent="space-between" mb="$4">
                  {calendarDays
                    .slice(rowIndex * 7, rowIndex * 7 + 7)
                    .map((item, index) => {
                      const hasTask =
                        item.isCurrentMonth &&
                        FARMING_TASKS[item.fullDate]?.length > 0;
                      const selected = selectedDate === item.fullDate;

                      return (
                        <VStack key={index} alignItems="center" w={40}>
                          <Pressable
                            onPress={() =>
                              item.isCurrentMonth &&
                              setSelectedDate(item.fullDate)
                            }
                          >
                            <Box
                              w={28}
                              h={28}
                              alignItems="center"
                              justifyContent="center"
                              rounded="$md"
                              borderWidth={selected || isToday(item) ? 2 : 0}
                              borderColor={selected ? "$red600" : "$green600"}
                              bg={selected ? "$red100" : "transparent"}
                            >
                              <Text
                                color={
                                  item.isCurrentMonth
                                    ? "$black"
                                    : "$coolGray400"
                                }
                                fontWeight={isToday(item) ? "$bold" : "$normal"}
                              >
                                {item.day}
                              </Text>
                            </Box>

                            {/* Task indicator */}
                            {hasTask && (
                              <Box
                                mt="$1"
                                w={selected ? 6 : 4}
                                h={selected ? 6 : 4}
                                bg={selected ? "$red400" : "$red600"}
                                rounded="$full"
                              />
                            )}
                          </Pressable>
                        </VStack>
                      );
                    })}
                </HStack>
              )
            )}
          </VStack>
        </VStack>
      </BaseCard>

      {/* Selected Day Tasks */}
      {selectedDate && (
        <BaseCard mt="$4" p="$4">
          <Text fontSize="$lg" fontWeight="$bold" mb="$2">
            Tasks for {selectedDate}:
          </Text>
          <ScrollView style={{ maxHeight: 150 }}>
            {FARMING_TASKS[selectedDate]?.map((task, idx) => (
              <Text key={idx} mb="$1">
                • {task}
              </Text>
            )) || <Text>No tasks for this day.</Text>}
          </ScrollView>
        </BaseCard>
      )}
    </SafeAreaView>
  );
}
