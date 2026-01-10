import { GET } from "lib/api/client";

interface WeatherForecastInput {
  latitude: number;
  longitude: number;
  days?: number;
}

export interface DailyWeather {
  datetime: string;
  weekdate: string;
  rainfall_mm: string;
  temperature_c: string;
  dewpoint_c: string;
  pressure_pa: string;
  wind_u10: string;
  wind_v10: string;
  wind_speed_ms: string;
  wind_speed_kmh: string;
  wind_direction_deg: string;
  wind_direction: string;
  weather: string;
}

export async function getWeatherForecast(
  params: WeatherForecastInput
): Promise<DailyWeather[]> {
  return GET<DailyWeather[]>(
    "/api/weather/forecast/latest?latitude=" +
      params.latitude +
      "&longitude=" +
      params.longitude +
      (params.days ? "&days=" + params.days : "")
  );
}
