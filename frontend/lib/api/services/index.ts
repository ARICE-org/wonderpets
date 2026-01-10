/**
 * API Services Barrel Export
 * Centralized export for all API service modules
 */

// Soil Forecast Service
export { soilForecastService, getForecast, getHealthScore, getReadingHistory, uploadReading } from './soil-forecast.service';

export type {
  SoilForecastResponse,
  HealthScoreResponse,
  ReadingHistoryResponse,
  ReadingHistoryEntry,
  SensorReading,
  UploadReadingResponse,
  WeeklyForecastData,
  ForecastSummary,
  NextReading,
  CurrentSoilMetric,
  SoilHealthStatus,
} from './soil-forecast.types';

// Soil Data Service (CSV upload and aggregation)
export { soilDataService, createSoilData, bulkUploadSoilData } from './soil-data.service';

export type {
  SoilReadingItem,
  WeeklyForecastItem,
  SoilDataCreateRequest,
  SoilDataResponse,
  SoilForecastReadingRequest,
  SoilForecastReadingResponse,
  SoilDataBulkUploadRequest,
  SoilDataBulkUploadResponse,
} from './soil-data.service';

// Sensors Service
export { sensorsService, listSoilSensors } from './sensors.service';

export type { SoilSensorDevice, ListSoilSensorsParams } from './sensors.service';
