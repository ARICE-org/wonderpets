/**
 * Sensors Service
 * Fetches soil sensor devices from the backend
 */

import { GET } from '../client';

export interface SoilSensorDevice {
  sensorId: string;
  sensorDesc: string;
  deviceStatus: boolean;
  createdDate?: string;
  updatedDate?: string;
}

export interface ListSoilSensorsParams {
  [key: string]: string | number | boolean | undefined;
  skip?: number;
  limit?: number;
  status?: boolean;
  search?: string;
}

/**
 * List soil sensors
 * GET /api/sensors
 */
export async function listSoilSensors(
  params?: ListSoilSensorsParams
): Promise<SoilSensorDevice[]> {
  return GET<SoilSensorDevice[]>('/api/sensors', { params });
}

export const sensorsService = {
  listSoilSensors,
};

export default sensorsService;
