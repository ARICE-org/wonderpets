/**
 * API Configuration
 * Centralized configuration for the API client
 */

export const API_CONFIG = {
  /**
   * Base URL for all API requests
   * Uses EXPO_PUBLIC_API_URL environment variable or defaults to localhost
   */
  BASE_URL: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',

  /**
   * Default request timeout in milliseconds (30 seconds)
   */
  TIMEOUT: 30000,

  /**
   * Default headers sent with every request
   */
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
} as const;

export type ApiConfig = typeof API_CONFIG;
