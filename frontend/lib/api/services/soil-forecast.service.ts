import { GET, POST } from '../client';
import type { RequestConfig } from '../types';
import type {
  SoilForecastResponse,
  HealthScoreResponse,
  ReadingHistoryResponse,
  SensorReading,
  UploadReadingResponse,
  WeeklyForecastData,
} from './soil-forecast.types';

/**
 * Fetch soil forecast data for a specific farmer
 */
export async function getForecast(
  farmerId: string,
  config?: RequestConfig
): Promise<SoilForecastResponse> {
  return GET<SoilForecastResponse>(`/api/soil-forecast/forecast/${farmerId}`, config);
}

/**
 * Fetch current health score for a farmer
 */
export async function getHealthScore(
  farmerId: string,
  config?: RequestConfig
): Promise<HealthScoreResponse> {
  return GET<HealthScoreResponse>(`/api/soil-forecast/health/${farmerId}`, config);
}

/**
 * Fetch reading history for a farmer
 */
export async function getReadingHistory(
  farmerId: string,
  limit?: number,
  offset?: number,
  config?: RequestConfig
): Promise<ReadingHistoryResponse> {
  return GET<ReadingHistoryResponse>(`/api/soil-forecast/history/${farmerId}`, {
    ...config,
    params: {
      ...(config?.params || {}),
      ...(limit && { limit }),
      ...(offset && { offset }),
    },
  });
}

/**
 * Upload new sensor readings and get updated forecast
 */
export async function uploadReading(
  reading: SensorReading,
  config?: RequestConfig
): Promise<UploadReadingResponse> {
  return POST<UploadReadingResponse, SensorReading>('/api/soil-forecast/readings', reading, config);
}

/**
 * Fetch soil forecast for the current week specifically
 */
export async function getWeeklyForecast(
  farmerId: string,
  config?: RequestConfig
): Promise<WeeklyForecastData> {
  return GET<WeeklyForecastData>(`/api/soil-forecast/weekly-forecast/${farmerId}`, config);
}

/**
 * Service object aggregating all soil forecast methods
 */
export const soilForecastService = {
  getForecast,
  getHealthScore,
  getReadingHistory,
  getWeeklyForecast,
  uploadReading,
};

export default soilForecastService;
