/**
 * Request/Response Interceptors
 * Handles authentication tokens and request/response transformations
 */

/**
 * Request interceptor function type
 * Receives the request config and can modify it before sending
 */
export type RequestInterceptor = (
  config: RequestInit & { url: string }
) => Promise<RequestInit & { url: string }> | (RequestInit & { url: string });

/**
 * Response interceptor function type
 * Receives the response and can modify it or trigger side effects
 */
export type ResponseInterceptor = (response: Response) => Promise<Response> | Response;

// In-memory storage for auth token
// For production, consider using expo-secure-store
let authToken: string | null = null;

// Callback for handling unauthorized responses
let onUnauthorizedCallback: (() => void) | null = null;

/**
 * Set the authentication token
 * The token will be automatically added to all subsequent requests
 */
export function setAuthToken(token: string | null): void {
  authToken = token;
}

/**
 * Get the current authentication token
 */
export function getAuthToken(): string | null {
  return authToken;
}

/**
 * Clear the authentication token
 */
export function clearAuthToken(): void {
  authToken = null;
}

/**
 * Check if user is currently authenticated
 */
export function isAuthenticated(): boolean {
  return authToken !== null;
}

/**
 * Set a callback to be invoked when a 401 response is received
 * Useful for triggering logout or navigation to login screen
 */
export function setOnUnauthorized(callback: (() => void) | null): void {
  onUnauthorizedCallback = callback;
}

/**
 * Request interceptor that adds Authorization header
 * Automatically attaches the Bearer token if available
 */
export const authRequestInterceptor: RequestInterceptor = (config) => {
  const token = getAuthToken();

  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`,
    };
  }

  return config;
};

/**
 * Response interceptor for handling 401 errors
 * Clears the token and triggers the unauthorized callback
 */
export const authResponseInterceptor: ResponseInterceptor = async (response) => {
  if (response.status === 401) {
    // Token expired or invalid - clear it
    clearAuthToken();

    // Trigger the unauthorized callback if set
    if (onUnauthorizedCallback) {
      onUnauthorizedCallback();
    }
  }

  return response;
};

/**
 * Array of request interceptors to be applied in order
 * Add additional interceptors here (e.g., logging, analytics)
 */
export const requestInterceptors: RequestInterceptor[] = [
  authRequestInterceptor,
];

/**
 * Array of response interceptors to be applied in order
 * Add additional interceptors here (e.g., logging, error tracking)
 */
export const responseInterceptors: ResponseInterceptor[] = [
  authResponseInterceptor,
];
