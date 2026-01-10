/**
 * API Client Module
 * Centralized HTTP client for making API requests
 *
 * @example
 * // Basic usage
 * import { get, post, setAuthToken } from '@/lib/api';
 *
 * // GET request with typed response
 * const user = await get<User>('/api/v1/users/123');
 *
 * // POST request with typed body and response
 * const newUser = await post<User, CreateUserDto>('/api/v1/users', { name: 'John' });
 *
 * // Set auth token (automatically attached to all requests)
 * setAuthToken(token);
 *
 * // Error handling
 * import { isApiError } from '@/lib/api';
 * try {
 *   const data = await get('/api/v1/data');
 * } catch (error) {
 *   if (isApiError(error) && error.isUnauthorized) {
 *     // Handle 401
 *   }
 * }
 */

// Core HTTP methods
export { get, post, put, patch, del, request } from './client';

// Types
export type {
  HttpMethod,
  RequestConfig,
  RequestOptions,
  ApiResponse,
  PaginatedResponse,
  Timestamps,
  BaseEntity,
} from './types';

// Error handling
export { ApiError, isApiError } from './errors';
export type { ApiErrorResponse } from './errors';

// Auth/Interceptors
export {
  setAuthToken,
  getAuthToken,
  clearAuthToken,
  isAuthenticated,
  setOnUnauthorized,
} from './interceptors';

export type { RequestInterceptor, ResponseInterceptor } from './interceptors';

// Configuration
export { API_CONFIG } from './config';
export type { ApiConfig } from './config';
