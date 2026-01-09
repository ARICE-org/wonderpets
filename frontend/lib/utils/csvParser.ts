/**
 * CSV Parser Utility for Soil Sensor Data
 * Parses CSV files and converts to JSON format for API submission
 */

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

export interface ParsedCsvResult {
  success: boolean;
  data: CsvSoilReading[];
  errors: string[];
  rowCount: number;
}

/**
 * Expected CSV columns (case-insensitive)
 */
const EXPECTED_COLUMNS = {
  timestamp: ['timestamp', 'datetime', 'date_time', 'time', 'recorded_at'],
  moisture: ['moisture', 'soil_moisture', 'soilmoisture', 'moisture_level', 'moisture_pct'],
  pH: ['ph', 'soil_ph', 'soilph', 'ph_level', 'acidity'],
  nitrogen: ['nitrogen', 'n', 'nitrogen_level', 'nitrogenlevel', 'n_ppm', 'nitrogen_ppm'],
  phosphorus: ['phosphorus', 'p', 'phosphorus_level', 'phosphoruslevel', 'p_ppm', 'phosphorus_ppm'],
  potassium: ['potassium', 'k', 'potassium_level', 'potassiumlevel', 'k_meq', 'potassium_meq'],
  organicMatter: ['organic_matter', 'organicmatter', 'organic', 'om', 'organic_pct'],
  temperature: ['temperature', 'temp', 'soil_temp', 'soiltemperature'],
};

/**
 * Find the actual column name in the CSV header that matches our expected column
 */
function findColumn(headers: string[], expectedNames: string[]): string | null {
  const normalizedHeaders = headers.map((h) => h.toLowerCase().trim());
  for (const expected of expectedNames) {
    const index = normalizedHeaders.indexOf(expected.toLowerCase());
    if (index !== -1) {
      return headers[index];
    }
  }
  return null;
}

/**
 * Parse a number value, handling empty strings and invalid values
 */
function parseNumber(value: string | undefined, defaultValue: number = 0): number {
  if (!value || value.trim() === '') {
    return defaultValue;
  }
  const parsed = parseFloat(value.trim());
  return isNaN(parsed) ? defaultValue : parsed;
}

/**
 * Parse a timestamp value, handling various formats
 */
function parseTimestamp(value: string | undefined): string {
  if (!value || value.trim() === '') {
    return new Date().toISOString();
  }

  const trimmed = value.trim();
  
  // Try parsing as ISO string
  const parsed = new Date(trimmed);
  if (!isNaN(parsed.getTime())) {
    return parsed.toISOString();
  }

  // Default to current time if parsing fails
  return new Date().toISOString();
}

/**
 * Parse CSV content string into structured data
 */
export function parseCsvContent(csvContent: string): ParsedCsvResult {
  const errors: string[] = [];
  const data: CsvSoilReading[] = [];

  // Split into lines and filter empty lines
  const lines = csvContent
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  if (lines.length < 2) {
    return {
      success: false,
      data: [],
      errors: ['CSV file must contain at least a header row and one data row'],
      rowCount: 0,
    };
  }

  // Parse header
  const headers = lines[0].split(',').map((h) => h.trim());

  // Map columns
  const columnMap = {
    timestamp: findColumn(headers, EXPECTED_COLUMNS.timestamp),
    moisture: findColumn(headers, EXPECTED_COLUMNS.moisture),
    pH: findColumn(headers, EXPECTED_COLUMNS.pH),
    nitrogen: findColumn(headers, EXPECTED_COLUMNS.nitrogen),
    phosphorus: findColumn(headers, EXPECTED_COLUMNS.phosphorus),
    potassium: findColumn(headers, EXPECTED_COLUMNS.potassium),
    organicMatter: findColumn(headers, EXPECTED_COLUMNS.organicMatter),
    temperature: findColumn(headers, EXPECTED_COLUMNS.temperature),
  };

  // Validate required columns
  const requiredColumns: (keyof typeof columnMap)[] = ['moisture', 'pH', 'nitrogen', 'phosphorus', 'potassium'];
  const missingColumns = requiredColumns.filter((col) => !columnMap[col]);

  if (missingColumns.length > 0) {
    return {
      success: false,
      data: [],
      errors: [`Missing required columns: ${missingColumns.join(', ')}`],
      rowCount: 0,
    };
  }

  // Parse data rows
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    const values = line.split(',').map((v) => v.trim());

    // Create value map
    const valueMap: Record<string, string> = {};
    headers.forEach((header, index) => {
      valueMap[header] = values[index] || '';
    });

    try {
      const reading: CsvSoilReading = {
        timestamp: parseTimestamp(columnMap.timestamp ? valueMap[columnMap.timestamp] : undefined),
        moisture: parseNumber(columnMap.moisture ? valueMap[columnMap.moisture] : undefined),
        pH: parseNumber(columnMap.pH ? valueMap[columnMap.pH] : undefined),
        nitrogen: parseNumber(columnMap.nitrogen ? valueMap[columnMap.nitrogen] : undefined),
        phosphorus: parseNumber(columnMap.phosphorus ? valueMap[columnMap.phosphorus] : undefined),
        potassium: parseNumber(columnMap.potassium ? valueMap[columnMap.potassium] : undefined),
        organicMatter: columnMap.organicMatter
          ? parseNumber(valueMap[columnMap.organicMatter], 0)
          : undefined,
        temperature: columnMap.temperature
          ? parseNumber(valueMap[columnMap.temperature], 0)
          : undefined,
      };

      // Validate ranges
      if (reading.pH < 0 || reading.pH > 14) {
        errors.push(`Row ${i + 1}: pH value ${reading.pH} is out of range (0-14)`);
      }
      if (reading.moisture < 0 || reading.moisture > 100) {
        errors.push(`Row ${i + 1}: moisture value ${reading.moisture} is out of range (0-100)`);
      }

      data.push(reading);
    } catch (err) {
      errors.push(`Row ${i + 1}: Failed to parse row - ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  }

  return {
    success: data.length > 0,
    data,
    errors,
    rowCount: data.length,
  };
}

/**
 * Calculate averages from parsed CSV data for aggregation
 */
export function calculateAverages(readings: CsvSoilReading[]): Omit<CsvSoilReading, 'timestamp'> & { timestamp: string } {
  if (readings.length === 0) {
    return {
      timestamp: new Date().toISOString(),
      moisture: 0,
      pH: 0,
      nitrogen: 0,
      phosphorus: 0,
      potassium: 0,
      organicMatter: 0,
      temperature: 0,
    };
  }

  const sum = readings.reduce(
    (acc, r) => ({
      moisture: acc.moisture + r.moisture,
      pH: acc.pH + r.pH,
      nitrogen: acc.nitrogen + r.nitrogen,
      phosphorus: acc.phosphorus + r.phosphorus,
      potassium: acc.potassium + r.potassium,
      organicMatter: acc.organicMatter + (r.organicMatter || 0),
      temperature: acc.temperature + (r.temperature || 0),
    }),
    { moisture: 0, pH: 0, nitrogen: 0, phosphorus: 0, potassium: 0, organicMatter: 0, temperature: 0 }
  );

  const count = readings.length;

  return {
    timestamp: new Date().toISOString(),
    moisture: Math.round((sum.moisture / count) * 100) / 100,
    pH: Math.round((sum.pH / count) * 100) / 100,
    nitrogen: Math.round((sum.nitrogen / count) * 100) / 100,
    phosphorus: Math.round((sum.phosphorus / count) * 100) / 100,
    potassium: Math.round((sum.potassium / count) * 100) / 100,
    organicMatter: Math.round((sum.organicMatter / count) * 100) / 100,
    temperature: Math.round((sum.temperature / count) * 100) / 100,
  };
}
