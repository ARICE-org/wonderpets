import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  HStack,
  ScrollView,
  Spinner,
  Text,
  VStack,
} from "@gluestack-ui/themed";
import WeatherCard from "./weathercard";

// Backend API configuration
const API_BASE_URL = "http://10.0.2.2:8000"; // Use 10.0.2.2 for Android emulator, localhost for iOS

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

export default function WeatherForecast({ data }: WeatherForecastProps) {
  const [apiData, setApiData] = useState<ForecastDay[] | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchWeatherData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${API_BASE_URL}/api/weather/forecast/latest?latitude=13.657096&longitude=123.224535&days=7`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const forecast: WeatherApiForecast[] = await response.json();
      const mapped: ForecastDay[] = forecast.map((f, index) => {
        const dayLabel =
          index === 0 ? "TODAY" : f.weekdate.slice(0, 3).toUpperCase();
        const tempValue = Math.round(
          parseFloat(f.temperature_c.replace(" °C", ""))
        );

        return {
          day: dayLabel,
          temp: `${tempValue}°C`,
          wind: f.wind_speed_kmh,
        };
      });

      setApiData(mapped);
    } catch (e) {
      // Fall back to provided data if API fails
      setApiData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchWeatherData();
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

      {loading && !displayData.length ? (
        <VStack px="$4" py="$3" alignItems="flex-start">
          <Spinner size="small" color="$black" />
        </VStack>
      ) : (
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
      )}
    </>
  );
}
