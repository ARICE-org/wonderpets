/**
 * Soil Forecast API Type Definitions
 * Types for soil health forecasting endpoints
 */

/**
 * Weekly forecast data for a specific week
 */
export interface WeeklyForecastData {
  week: number;
  date: string;
  nitrogenPpm: number;
  phosphorusPpm: number;
  potassiumMeq: number;
  pH: number;
  soilMoisturePct: number;
  organicMatterPct: number;
  healthScore: number;
  healthCategory: 'Excellent' | 'Good' | 'Fair' | 'Poor';
  realigned: boolean;
  correctionApplied: string | null;
}

/**
 * Forecast summary containing overall health information
 */
export interface ForecastSummary {
  forecastId: string;
  farmerId: string;
  plantingDate: string;
  forecastStart: string;
  forecastEnd: string;
  totalWeeks: number;
  averageHealthScore: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  createdAt: string;
  lastUpdated: string;
  realignmentCount: number;
}

/**
 * Recommended next reading information
 */
export interface NextReading {
  recommendedDate: string;
  daysFromNow: number;
  reason: string;
}

/**
 * Complete soil forecast response from backend
 */
export interface SoilForecastResponse {
  forecastSummary: ForecastSummary;
  weeklyForecast: WeeklyForecastData[];
  currentHealthScore: number;
  currentHealthCategory: 'Excellent' | 'Good' | 'Fair' | 'Poor';
  lastReadingDate: string;
  nextReading: NextReading;
}

/**
 * Current soil metric for display
 */
export interface CurrentSoilMetric {
  id: string;
  label: string;
  value: number | string;
  unit: string;
  status: 'good' | 'warning' | 'bad';
  color: string;
  timestamp: string;
}

/**
 * Soil health status for quick reference
 */
export interface SoilHealthStatus {
  score: number;
  category: 'Excellent' | 'Good' | 'Fair' | 'Poor';
  trend: 'increasing' | 'decreasing' | 'stable';
  lastUpdated: string;
  nextReadingDue: string;
}

/**
 * Health score response from GET /api/soil-forecast/health/{farmer_id}
 */
export interface HealthScoreResponse {
  healthScore: number;
  healthCategory: 'Excellent' | 'Good' | 'Fair' | 'Poor';
  lastUpdated: string;
  nextRecommendedReading: string;
}

/**
 * Single reading history entry
 */
export interface ReadingHistoryEntry {
  id: string;
  date: string;
  nitrogenPpm: number;
  phosphorusPpm: number;
  potassiumMeq: number;
  pH: number;
  soilMoisturePct: number;
  organicMatterPct: number;
  healthScore: number;
  healthCategory: 'Excellent' | 'Good' | 'Fair' | 'Poor';
}

/**
 * Reading history response from GET /api/soil-forecast/history/{farmer_id}
 */
export interface ReadingHistoryResponse {
  farmerId: string;
  readings: ReadingHistoryEntry[];
  totalReadings: number;
}

/**
 * Sensor reading data to upload
 */
export interface SensorReading {
  farmerId: string;
  nitrogenPpm: number;
  phosphorusPpm: number;
  potassiumMeq: number;
  pH: number;
  soilMoisturePct: number;
  organicMatterPct: number;
  recordedAt?: string; // ISO date string, defaults to now if not provided
}

/**
 * Response from POST /api/soil-forecast/readings
 */
export interface UploadReadingResponse {
  success: boolean;
  message: string;
  reading: ReadingHistoryEntry;
  forecast: SoilForecastResponse;
}
