import { GET, POST } from '../client';
import type {
  SoilForecastResponse,
  HealthScoreResponse,
  ReadingHistoryResponse,
  SensorReading,
  UploadReadingResponse,
} from './soil-forecast.types';

/**
 * Fetch soil forecast data for a specific farmer
 * GET /api/soil-forecast/forecast/{farmerId}
 * 
 * @param farmerId - The farmer's unique identifier
 * @returns Promise resolving to the complete soil forecast data
 *
 * @example
 * const forecast = await soilForecastService.getForecast('b4c478ad-ca81-4576-aed1-0a6f828b8602');
 * console.log(forecast.currentHealthScore);
 */
export async function getForecast(farmerId: string): Promise<SoilForecastResponse> {
  return GET<SoilForecastResponse>(`/api/soil-forecast/forecast/${farmerId}`);
}

/**
 * Fetch current health score for a farmer
 * GET /api/soil-forecast/health/{farmerId}
 * 
 * @param farmerId - The farmer's unique identifier
 * @returns Promise resolving to the current health score and category
 *
 * @example
 * const health = await soilForecastService.getHealthScore('farmer-id-123');
 * console.log(`Health: ${health.healthScore} - ${health.healthCategory}`);
 */
export async function getHealthScore(farmerId: string): Promise<HealthScoreResponse> {
  return GET<HealthScoreResponse>(`/api/soil-forecast/health/${farmerId}`);
}

/**
 * Fetch reading history for a farmer
 * GET /api/soil-forecast/history/{farmerId}
 * 
 * @param farmerId - The farmer's unique identifier
 * @param limit - Optional: limit number of readings returned
 * @param offset - Optional: offset for pagination
 * @returns Promise resolving to the reading history
 *
 * @example
 * const history = await soilForecastService.getReadingHistory('farmer-id-123');
 * console.log(`Total readings: ${history.totalReadings}`);
 */
export async function getReadingHistory(
  farmerId: string,
  limit?: number,
  offset?: number
): Promise<ReadingHistoryResponse> {
  return GET<ReadingHistoryResponse>(`/api/soil-forecast/history/${farmerId}`, {
    params: {
      ...(limit && { limit }),
      ...(offset && { offset }),
    },
  });
}

/**
 * Upload new sensor readings and get updated forecast
 * POST /api/soil-forecast/readings
 * 
 * @param reading - The sensor reading data to upload
 * @returns Promise resolving to the uploaded reading and updated forecast
 *
 * @example
 * const result = await soilForecastService.uploadReading({
 *   farmerId: 'farmer-id-123',
 *   nitrogenPpm: 50.5,
 *   phosphorusPpm: 3.8,
 *   potassiumMeq: 0.75,
 *   pH: 5.8,
 *   soilMoisturePct: 22.5,
 *   organicMatterPct: 3.1,
 * });
 * 
 * console.log(`New health score: ${result.forecast.currentHealthScore}`);
 */
export async function uploadReading(reading: SensorReading): Promise<UploadReadingResponse> {
  return POST<UploadReadingResponse, SensorReading>('/api/soil-forecast/readings', reading);
}

/**
 * Service object aggregating all soil forecast methods
 */
export const soilForecastService = {
  getForecast,
  getHealthScore,
  getReadingHistory,
  uploadReading,
};

export default soilForecastService;
