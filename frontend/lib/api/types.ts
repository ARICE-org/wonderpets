/**
 * API Type Definitions
 * TypeScript interfaces and types for the API client
 */

/**
 * Supported HTTP methods
 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH';

/**
 * Configuration options for individual requests
 */
export interface RequestConfig {
  /** Additional headers to include with the request */
  headers?: Record<string, string>;
  /** Query parameters to append to the URL */
  params?: Record<string, string | number | boolean | undefined>;
  /** Request timeout in milliseconds (overrides default) */
  timeout?: number;
  /** AbortSignal for request cancellation */
  signal?: AbortSignal;
}

/**
 * Full request options including method and endpoint
 */
export interface RequestOptions<TBody = unknown> extends RequestConfig {
  method: HttpMethod;
  endpoint: string;
  body?: TBody;
}

/**
 * Standard API response wrapper
 * Use this if your backend wraps responses in a standard format
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/**
 * Paginated response type for list endpoints
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * Common entity timestamps
 */
export interface Timestamps {
  created_at: string;
  updated_at: string;
}

/**
 * Base entity with ID
 */
export interface BaseEntity extends Timestamps {
  id: string | number;
}
