/**
 * API Client
 * Core HTTP client with request/response handling
 */

import { API_CONFIG } from './config';
import { ApiError } from './errors';
import type { RequestOptions } from './types';
import { requestInterceptors, responseInterceptors } from './interceptors';
import { toastService } from '../services/toast.service';

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
    message = errorData.message || errorData.detail || message;
    detail = errorData.detail || errorData;
    code = errorData.code;
  } catch {
    try {
      const textContent = await response.text();
      if (textContent) {
        message = textContent;
      }
    } catch {
      // Ignored
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
 */
async function request<TResponse, TBody = unknown>(
  options: RequestOptions<TBody>
): Promise<TResponse> {
  const {
    method,
    endpoint,
    body,
    headers,
    params,
    timeout,
    signal,
    toastUploadingMessage,
    toastSuccessMessage,
    toastErrorMessage,
    onSuccess,
    onError
  } = options;

  const url = buildUrl(endpoint, params);

  let config: RequestInit & { url: string } = {
    url,
    method,
    headers: {
      ...API_CONFIG.DEFAULT_HEADERS,
      ...headers,
    },
  };

  if (body !== undefined && method !== 'GET') {
    config.body = JSON.stringify(body);
  }

  for (const interceptor of requestInterceptors) {
    config = await interceptor(config);
  }

  const controller = new AbortController();
  const timeoutDuration = timeout || API_CONFIG.TIMEOUT;
  const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);

  if (signal) {
    signal.addEventListener('abort', () => controller.abort());
  }

  let loadingToastId: string | null = null;
  if (toastUploadingMessage) {
    loadingToastId = toastService.showLoading(toastUploadingMessage);
  }

  try {
    let response = await fetch(config.url, {
      ...config,
      signal: controller.signal,
    });

    for (const interceptor of responseInterceptors) {
      response = await interceptor(response);
    }

    if (!response.ok) {
      throw await parseErrorResponse(response);
    }

    let data: any;

    if (response.status === 204) {
      data = undefined;
    } else {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }
    }

    const typedData = data as TResponse;

    if (loadingToastId) toastService.close(loadingToastId);
    if (toastSuccessMessage) {
      toastService.showSuccess(toastSuccessMessage);
    }
    if (onSuccess) onSuccess(typedData);

    return typedData;
  } catch (error) {
    if (loadingToastId) toastService.close(loadingToastId);

    const finalErrorMessage = toastErrorMessage || (error instanceof ApiError ? error.message : 'An error occurred');
    if (toastErrorMessage || (error instanceof ApiError && error.status !== 0)) {
      toastService.showError(finalErrorMessage);
    }

    if (onError) onError(error);

    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError({
        status: 0,
        message: 'Request timeout',
        code: 'TIMEOUT',
      });
    }

    if (error instanceof TypeError && error.message === 'Network request failed') {
      throw new ApiError({
        status: 0,
        message: 'Network error. Please check your connection.',
        code: 'NETWORK_ERROR',
      });
    }

    if (error instanceof ApiError) {
      throw error;
    }

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

export { request };
