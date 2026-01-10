/**
 * Soil Data Service
 * Handles soil data API calls for CSV upload and aggregation
 */

import { POST } from '../client';
import type { RequestConfig } from '../types';

/**
 * Single reading item for API requests
 */
export interface SoilReadingItem {
  timestamp: string;
  moisture: number;
  pH: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  organicMatter?: number;
  temperature?: number;
}

/**
 * Weekly forecast item from response
 */
export interface WeeklyForecastItem {
  week: number;
  date: string;
  healthScore: number;
  healthCategory: string;
}

/**
 * Request payload for creating soil data (aggregated from CSV)
 */
export interface SoilDataCreateRequest {
  dateTimeStamp: string;
  soilMoisture: number;
  soilPh: number;
  nitrogenLevel: number;
  phosphorusLevel: number;
  potassiumLevel: number;
  sensorId: string;
}

/**
 * Response from soil data creation
 */
export interface SoilDataResponse {
  soilId: string;
  dateTimeStamp: string;
  soilMoisture: number;
  soilPh: number;
  nitrogenLevel: number;
  phosphorusLevel: number;
  potassiumLevel: number;
  sensorId: string;
}

/**
 * Request payload for uploading to soil-forecast/readings
 */
export interface SoilForecastReadingRequest {
  farmerId: string;
  plantingDate: string;
  sensorId?: string;
  readings: SoilReadingItem[];
}

/**
 * Response from soil forecast readings upload
 */
export interface SoilForecastReadingResponse {
  forecastSummary: {
    forecastId: string;
    farmerId: string;
    plantingDate: string;
    averageHealthScore: number;
    trend: string;
  };
  weeklyForecast: WeeklyForecastItem[];
  currentHealthScore: number;
  currentHealthCategory: string;
}

/**
 * Bulk upload request for CSV-parsed data
 * Contains raw readings that backend will aggregate
 */
export interface SoilDataBulkUploadRequest {
  sensorId: string;
  farmerId: string;
  plantingDate: string;
  readings: SoilReadingItem[];
}

/**
 * Response from bulk upload with chained forecast
 */
export interface SoilDataBulkUploadResponse {
  soilData: SoilDataResponse;
  forecast: SoilForecastReadingResponse;
  message: string;
}

/**
 * Upload aggregated soil data from CSV
 */
export async function createSoilData(
  data: SoilDataCreateRequest,
  config?: RequestConfig
): Promise<SoilDataResponse> {
  return POST<SoilDataResponse, SoilDataCreateRequest>('/api/soil-data', data, config);
}

/**
 * Bulk upload CSV-parsed readings
 */
export async function bulkUploadSoilData(
  data: SoilDataBulkUploadRequest,
  config?: RequestConfig
): Promise<SoilDataBulkUploadResponse> {
  return POST<SoilDataBulkUploadResponse, SoilDataBulkUploadRequest>(
    '/api/soil-data/bulk-upload',
    data,
    config
  );
}

/**
 * Service object aggregating all soil data methods
 */
export const soilDataService = {
  createSoilData,
  bulkUploadSoilData,
};

export default soilDataService;
