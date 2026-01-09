/**
 * API Client
 * Core HTTP client with request/response handling
 */

import { API_CONFIG } from './config';
import { ApiError } from './errors';
import type { RequestOptions } from './types';
import { requestInterceptors, responseInterceptors } from './interceptors';

/**
 * Build URL with query parameters
 */
function buildUrl(
  endpoint: string,
  params?: Record<string, string | number | boolean | undefined>
): string {
  // Handle absolute URLs vs relative endpoints
  const isAbsoluteUrl = endpoint.startsWith('http://') || endpoint.startsWith('https://');
  const url = isAbsoluteUrl ? new URL(endpoint) : new URL(endpoint, API_CONFIG.BASE_URL);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return url.toString();
}

/**
 * Parse error response from the server
 */
async function parseErrorResponse(response: Response): Promise<ApiError> {
  let message = `Request failed with status ${response.status}`;
  let detail: unknown;
  let code: string | undefined;

  try {
    const errorData = await response.json();
    // Handle FastAPI error format
    message = errorData.message || errorData.detail || message;
    detail = errorData.detail || errorData;
    code = errorData.code;
  } catch {
    // Response body is not JSON, try to read as text
    try {
      const textContent = await response.text();
      if (textContent) {
        message = textContent;
      }
    } catch {
      // Unable to read response body
    }
  }

  return new ApiError({
    status: response.status,
    message,
    detail,
    code,
  });
}

/**
 * Core request function with full configuration
 * Handles all HTTP requests with interceptors, error handling, and timeouts
 */
async function request<TResponse, TBody = unknown>(
  options: RequestOptions<TBody>
): Promise<TResponse> {
  const { method, endpoint, body, headers, params, timeout, signal } = options;

  // Build the full URL
  const url = buildUrl(endpoint, params);

  // Prepare request configuration
  let config: RequestInit & { url: string } = {
    url,
    method,
    headers: {
      ...API_CONFIG.DEFAULT_HEADERS,
      ...headers,
    },
  };

  // Add body for non-GET requests
  if (body !== undefined && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  // Apply request interceptors
  for (const interceptor of requestInterceptors) {
    config = await interceptor(config);
  }

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutDuration = timeout || API_CONFIG.TIMEOUT;
  const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);

  // Merge abort signals if one was provided
  if (signal) {
    signal.addEventListener('abort', () => controller.abort());
  }

  try {
    let response = await fetch(config.url, {
      ...config,
      signal: controller.signal,
    });

    // Apply response interceptors
    for (const interceptor of responseInterceptors) {
      response = await interceptor(response);
    }

    // Handle non-OK responses
    if (!response.ok) {
      throw await parseErrorResponse(response);
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return undefined as TResponse;
    }

    // Check content type before parsing
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      const data: TResponse = await response.json();
      return data;
    }

    // Return text for non-JSON responses
    const text = await response.text();
    return text as TResponse;
  } catch (error) {
    // Handle abort/timeout errors
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError({
        status: 0,
        message: 'Request timeout',
        code: 'TIMEOUT',
      });
    }

    // Handle network errors
    if (error instanceof TypeError && error.message === 'Network request failed') {
      throw new ApiError({
        status: 0,
        message: 'Network error. Please check your connection.',
        code: 'NETWORK_ERROR',
      });
    }

    // Re-throw ApiErrors as-is
    if (error instanceof ApiError) {
      throw error;
    }

    // Wrap unknown errors
    throw new ApiError({
      status: 0,
      message: error instanceof Error ? error.message : 'An unknown error occurred',
      code: 'UNKNOWN_ERROR',
    });
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * HTTP GET request
 * @param endpoint - API endpoint (relative or absolute URL)
 * @param config - Optional request configuration
 * @returns Promise resolving to the typed response
 *
 * @example
 * const user = await GET<User>('/api/v1/users/123');
 * const users = await GET<User[]>('/api/v1/users', { params: { page: 1 } });
 */
export async function GET<TResponse>(
  endpoint: string,
  config?: Omit<RequestOptions, 'method' | 'endpoint' | 'body'>
): Promise<TResponse> {
  return request<TResponse>({
    method: 'GET',
    endpoint,
    ...config,
  });
}

/**
 * HTTP POST request
 * @param endpoint - API endpoint (relative or absolute URL)
 * @param body - Request body to be JSON serialized
 * @param config - Optional request configuration
 * @returns Promise resolving to the typed response
 *
 * @example
 * const user = await POST<User, CreateUserDto>('/api/v1/users', { name: 'John' });
 */
export async function POST<TResponse, TBody = unknown>(
  endpoint: string,
  body?: TBody,
  config?: Omit<RequestOptions, 'method' | 'endpoint' | 'body'>
): Promise<TResponse> {
  return request<TResponse, TBody>({
    method: 'POST',
    endpoint,
    body,
    ...config,
  });
}

/**
 * HTTP PUT request
 * @param endpoint - API endpoint (relative or absolute URL)
 * @param body - Request body to be JSON serialized
 * @param config - Optional request configuration
 * @returns Promise resolving to the typed response
 *
 * @example
 * const user = await PUT<User, UpdateUserDto>('/api/v1/users/123', { name: 'Jane' });
 */
export async function PUT<TResponse, TBody = unknown>(
  endpoint: string,
  body?: TBody,
  config?: Omit<RequestOptions, 'method' | 'endpoint' | 'body'>
): Promise<TResponse> {
  return request<TResponse, TBody>({
    method: 'PUT',
    endpoint,
    body,
    ...config,
  });
}

/**
 * HTTP PATCH request
 * @param endpoint - API endpoint (relative or absolute URL)
 * @param body - Request body to be JSON serialized
 * @param config - Optional request configuration
 * @returns Promise resolving to the typed response
 *
 * @example
 * const user = await PATCH<User, Partial<User>>('/api/v1/users/123', { name: 'Jane' });
 */
export async function PATCH<TResponse, TBody = unknown>(
  endpoint: string,
  body?: TBody,
  config?: Omit<RequestOptions, 'method' | 'endpoint' | 'body'>
): Promise<TResponse> {
  return request<TResponse, TBody>({
    method: 'PATCH',
    endpoint,
    body,
    ...config,
  });
}

/**
 * HTTP DELETE request
 * @param endpoint - API endpoint (relative or absolute URL)
 * @param config - Optional request configuration
 * @returns Promise resolving to the typed response (often void)
 *
 * @example
 * await DELETE('/api/v1/users/123');
 * const result = await DELETE<DeleteResponse>('/api/v1/users/123');
 */
export async function DELETE<TResponse = void>(
  endpoint: string,
  config?: Omit<RequestOptions, 'method' | 'endpoint' | 'body'>
): Promise<TResponse> {
  return request<TResponse>({
    method: 'DELETE',
    endpoint,
    ...config,
  });
}

// Export the raw request function for advanced use cases
export { request };
