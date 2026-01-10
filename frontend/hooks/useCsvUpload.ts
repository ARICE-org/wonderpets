/**
 * useCSVUpload Hook
 * Handles CSV file selection, parsing, and upload for soil sensor data
 * Uses papaparse for reliable CSV parsing
 */

import { useState, useCallback } from 'react';
import * as DocumentPicker from 'expo-document-picker';
import Papa from 'papaparse';
import { soilDataService, type SoilDataBulkUploadRequest } from '../lib/api/services/soil-data.service';

export interface CsvSoilReading {
  timestamp: string;
  moisture: number;
  pH: number;
  nitrogen: number;
  phosphorus: number;
  potassium: number;
  organicMatter?: number;
  temperature?: number;
}

export interface CsvUploadState {
  isLoading: boolean;
  isParsing: boolean;
  isUploading: boolean;
  error: string | null;
  parsedData: CsvSoilReading[] | null;
  parseErrors: string[];
  rowCount: number;
}

export interface CsvUploadResult {
  success: boolean;
  message: string;
  data?: unknown;
}

export interface UseCsvUploadOptions {
  farmerId: string;
  sensorId: string;
  plantingDate: string;
  onSuccess?: (result: CsvUploadResult) => void;
  onError?: (error: string) => void;
}

// Column name mappings (case-insensitive)
const COLUMN_MAPPINGS: Record<string, string[]> = {
  timestamp: ['timestamp', 'datetime', 'date_time', 'time', 'recorded_at', 'date'],
  moisture: ['moisture', 'soil_moisture', 'soilmoisture', 'moisture_level', 'moisture_pct'],
  pH: ['ph', 'soil_ph', 'soilph', 'ph_level', 'acidity'],
  nitrogen: ['nitrogen', 'n', 'nitrogen_level', 'nitrogenlevel', 'n_ppm', 'nitrogen_ppm'],
  phosphorus: ['phosphorus', 'p', 'phosphorus_level', 'phosphoruslevel', 'p_ppm', 'phosphorus_ppm'],
  potassium: ['potassium', 'k', 'potassium_level', 'potassiumlevel', 'k_meq', 'potassium_meq'],
  organicMatter: ['organic_matter', 'organicmatter', 'organic', 'om', 'organic_pct'],
  temperature: ['temperature', 'temp', 'soil_temp', 'soiltemperature'],
};

function findColumnValue(row: Record<string, string>, targetField: string): string | undefined {
  const possibleNames = COLUMN_MAPPINGS[targetField] || [targetField];

  for (const name of possibleNames) {
    // Check exact match first
    if (row[name] !== undefined) return row[name];

    // Check case-insensitive
    const lowerName = name.toLowerCase();
    for (const key of Object.keys(row)) {
      if (key.toLowerCase() === lowerName) {
        return row[key];
      }
    }
  }
  return undefined;
}

function parseNumber(value: string | undefined, defaultValue: number = 0): number {
  if (!value || value.trim() === '') return defaultValue;
  const parsed = parseFloat(value.trim());
  return isNaN(parsed) ? defaultValue : parsed;
}

function parseTimestamp(value: string | undefined): string {
  if (!value || value.trim() === '') {
    return new Date().toISOString();
  }
  const parsed = new Date(value.trim());
  return isNaN(parsed.getTime()) ? new Date().toISOString() : parsed.toISOString();
}

export function useCsvUpload(options: UseCsvUploadOptions) {
  const { farmerId, sensorId, plantingDate, onSuccess, onError } = options;

  const [state, setState] = useState<CsvUploadState>({
    isLoading: false,
    isParsing: false,
    isUploading: false,
    error: null,
    parsedData: null,
    parseErrors: [],
    rowCount: 0,
  });

  /**
   * Pick and parse a CSV file using papaparse
   */
  const pickAndParseFile = useCallback(async () => {
    setState((prev) => ({ ...prev, isLoading: true, isParsing: true, error: null }));

    try {
      // Pick the document
      const result = await DocumentPicker.getDocumentAsync({
        type: ['text/csv', 'text/comma-separated-values', 'application/csv', 'text/plain', '*/*'],
        copyToCacheDirectory: true,
      });

      if (result.canceled || !result.assets || result.assets.length === 0) {
        setState((prev) => ({ ...prev, isLoading: false, isParsing: false }));
        return null;
      }

      const file = result.assets[0];

      // Fetch the file content using the URI
      const response = await fetch(file.uri);
      const csvText = await response.text();

      // Parse with papaparse
      const parseResult = Papa.parse<Record<string, string>>(csvText, {
        header: true,
        skipEmptyLines: true,
        transformHeader: (header) => header.trim(),
      });

      if (parseResult.errors.length > 0) {
        const errorMessages = parseResult.errors.map((e) => e.message);
        setState((prev) => ({
          ...prev,
          isLoading: false,
          isParsing: false,
          error: errorMessages[0],
          parseErrors: errorMessages,
        }));
        return null;
      }

      // Transform to our data structure
      const readings: CsvSoilReading[] = [];
      const errors: string[] = [];

      parseResult.data.forEach((row, index) => {
        try {
          const reading: CsvSoilReading = {
            timestamp: parseTimestamp(findColumnValue(row, 'timestamp')),
            moisture: parseNumber(findColumnValue(row, 'moisture')),
            pH: parseNumber(findColumnValue(row, 'pH')),
            nitrogen: parseNumber(findColumnValue(row, 'nitrogen')),
            phosphorus: parseNumber(findColumnValue(row, 'phosphorus')),
            potassium: parseNumber(findColumnValue(row, 'potassium')),
            organicMatter: parseNumber(findColumnValue(row, 'organicMatter'), 3.0),
            temperature: parseNumber(findColumnValue(row, 'temperature'), 25),
          };

          // Basic validation
          if (reading.pH < 0 || reading.pH > 14) {
            errors.push(`Row ${index + 2}: pH value ${reading.pH} is out of range (0-14)`);
          }
          if (reading.moisture < 0 || reading.moisture > 100) {
            errors.push(`Row ${index + 2}: moisture value ${reading.moisture} is out of range (0-100)`);
          }

          readings.push(reading);
        } catch (err) {
          errors.push(`Row ${index + 2}: Failed to parse - ${err instanceof Error ? err.message : 'Unknown error'}`);
        }
      });

      if (readings.length === 0) {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          isParsing: false,
          error: 'No valid readings found in CSV file',
          parseErrors: errors,
        }));
        return null;
      }

      setState((prev) => ({
        ...prev,
        isLoading: false,
        isParsing: false,
        parsedData: readings,
        parseErrors: errors,
        rowCount: readings.length,
        error: null,
      }));

      return {
        success: true,
        data: readings,
        errors,
        rowCount: readings.length,
      };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to read file';
      setState((prev) => ({
        ...prev,
        isLoading: false,
        isParsing: false,
        error: errorMessage,
      }));
      onError?.(errorMessage);
      return null;
    }
  }, [onError]);

  /**
   * Upload parsed data to the API
   */
  const uploadData = useCallback(
    async (data: CsvSoilReading[], sensorIdOverride?: string): Promise<CsvUploadResult> => {
      setState((prev) => ({ ...prev, isUploading: true, error: null }));

      try {
        const resolvedSensorId = sensorIdOverride || sensorId;
        if (!resolvedSensorId) {
          throw new Error('No sensor selected');
        }

        const request: SoilDataBulkUploadRequest = {
          farmerId,
          sensorId: resolvedSensorId,
          plantingDate,
          readings: data.map((r) => ({
            timestamp: r.timestamp,
            moisture: r.moisture,
            pH: r.pH,
            nitrogen: r.nitrogen,
            phosphorus: r.phosphorus,
            potassium: r.potassium,
            organicMatter: r.organicMatter,
            temperature: r.temperature,
          })),
        };

        const response = await soilDataService.bulkUploadSoilData(request, {
          toastUploadingMessage: 'Uploading CSV...',
          toastSuccessMessage: 'Soil data uploaded successfully',
          // toastErrorMessage: ... (client handles default)
        });

        const result: CsvUploadResult = {
          success: true,
          message: response.message || 'Soil data uploaded successfully',
          data: response,
        };

        setState((prev) => ({
          ...prev,
          isUploading: false,
          parsedData: null,
          rowCount: 0,
        }));

        onSuccess?.(result);
        return result;
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to upload data';
        setState((prev) => ({
          ...prev,
          isUploading: false,
          error: errorMessage,
        }));
        onError?.(errorMessage);
        return {
          success: false,
          message: errorMessage,
        };
      }
    },
    [farmerId, sensorId, plantingDate, onSuccess, onError]
  );

  /**
   * Combined pick, parse, and upload flow
   */
  const pickParseAndUpload = useCallback(async (sensorIdOverride?: string): Promise<CsvUploadResult> => {
    const parsed = await pickAndParseFile();

    if (!parsed || !parsed.success || parsed.data.length === 0) {
      return {
        success: false,
        message: parsed?.errors[0] || 'No data to upload',
      };
    }

    return uploadData(parsed.data, sensorIdOverride);
  }, [pickAndParseFile, uploadData]);

  /**
   * Reset state
   */
  const reset = useCallback(() => {
    setState({
      isLoading: false,
      isParsing: false,
      isUploading: false,
      error: null,
      parsedData: null,
      parseErrors: [],
      rowCount: 0,
    });
  }, []);

  return {
    ...state,
    pickAndParseFile,
    uploadData,
    pickParseAndUpload,
    reset,
  };
}
