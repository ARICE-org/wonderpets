import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  HStack,
  ScrollView,
  Spinner,
  Text,
  VStack,
  Box,
} from "@gluestack-ui/themed";
import WeatherCard from "./weathercard";
import BaseCard from "../baseCard";
import { getWeatherForecast } from "../../../../lib/api/services/weather/weather_forecast";

interface WeatherApiForecast {
  weekdate: string;
  temperature_c: string;
  wind_speed_kmh: string;
}

interface ForecastDay {
  day: string;
  temp: string;
  wind: string;
}

interface WeatherForecastProps {
  data?: ForecastDay[];
}

function ForecastSkeletonRow({ count = 7 }: { count?: number }) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
      <HStack px="$1">
        {Array.from({ length: count }).map((_, index) => {
          const isToday = index === 0;
          return (
            <BaseCard
              key={index}
              w={isToday ? 100 : 80}
              minHeight={128}
              mx="$1"
              my="$2"
              p="$3"
              rounded="$2xl"
              bg="$coolGray100"
              alignItems="center"
            >
              <Box
                h={18}
                w={isToday ? 64 : 52}
                bg="$coolGray200"
                rounded="$full"
              />
              <Box mt="$3" h={26} w={54} bg="$coolGray200" rounded="$md" />
              <Box mt="$2" h={30} w={30} bg="$coolGray200" rounded="$full" />
              <Box
                mt="$2"
                h={10}
                w={isToday ? 64 : 56}
                bg="$coolGray200"
                rounded="$md"
              />
            </BaseCard>
          );
        })}
      </HStack>
    </ScrollView>
  );
}

export default function WeatherForecast({ data }: WeatherForecastProps) {
  const [apiData, setApiData] = useState<ForecastDay[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [serverNotReady, setServerNotReady] = useState(false);
  const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryDelayRef = useRef(2000);

  const fetchWeatherData = useCallback(async () => {
    try {
      setLoading(true);
      setServerNotReady(false);

      const forecast = await getWeatherForecast({
        latitude: 13.657096,
        longitude: 123.224535,
        days: 7,
      });
      const mapped: ForecastDay[] = forecast.map((f: any, index: number) => {
        const dayLabel =
          index === 0 ? "TODAY" : f.weekdate.slice(0, 3).toUpperCase();
        const tempValue = Math.round(
          parseFloat(String(f.temperature_c).replace(" °C", ""))
        );
        return {
          day: dayLabel,
          temp: `${tempValue}°C`,
          wind: f.wind_speed_kmh,
        };
      });
      setApiData(mapped);
      retryDelayRef.current = 2000;
    } catch {
      // If the backend isn't reachable yet, keep a skeleton UI and retry.
      setServerNotReady(true);
      setApiData(null);

      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
      const delay = retryDelayRef.current;
      retryDelayRef.current = Math.min(10000, Math.round(delay * 1.6));
      retryTimerRef.current = setTimeout(() => {
        fetchWeatherData();
      }, delay);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWeatherData();
    return () => {
      if (retryTimerRef.current) clearTimeout(retryTimerRef.current);
    };
  }, [fetchWeatherData]);

  const displayData = useMemo(() => {
    if (apiData && apiData.length) return apiData;
    if (data && data.length) return data;
    return [];
  }, [apiData, data]);

  return (
    <>
      <HStack px="$4" alignItems="center" justifyContent="flex-start" mb="$2">
        <Text fontSize="$lg" fontWeight="$bold" color="$black">
          7 Day Forecast
        </Text>
      </HStack>

      {displayData.length ? (
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          <HStack px="$1">
            {displayData.map((day, index) => (
              <WeatherCard
                key={index}
                day={day.day}
                temperature={day.temp}
                wind={day.wind}
                isToday={day.day.toUpperCase() === "TODAY" || index === 0}
              />
            ))}
          </HStack>
        </ScrollView>
      ) : serverNotReady || loading ? (
        <VStack>
          <ForecastSkeletonRow />
          <HStack px="$4" alignItems="center" space="xs" mt="$1">
            <Spinner size="small" color="$black" />
            <Text fontSize="$xs" color="$coolGray600">
              Waiting for server…
            </Text>
          </HStack>
        </VStack>
      ) : (
        <VStack px="$4" py="$3">
          <Text fontSize="$sm" color="$coolGray600">
            No forecast available.
          </Text>
        </VStack>
      )}
    </>
  );
}
