/**
 * API Error Types and Classes
 * Centralized error handling for API responses
 */

export interface ApiErrorResponse {
  status: number;
  message: string;
  detail?: unknown;
  code?: string;
}

/**
 * Custom error class for API errors
 * Provides structured error information with helper methods
 */
export class ApiError extends Error {
  public readonly status: number;
  public readonly detail?: unknown;
  public readonly code?: string;
  public readonly isApiError = true;

  constructor({ status, message, detail, code }: ApiErrorResponse) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
    this.code = code;

    // Maintains proper stack trace for where error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ApiError);
    }
  }

  /**
   * Check if error matches a specific HTTP status
   */
  isStatus(status: number): boolean {
    return this.status === status;
  }

  /**
   * Returns true if this is a 401 Unauthorized error
   */
  get isUnauthorized(): boolean {
    return this.status === 401;
  }

  /**
   * Returns true if this is a 403 Forbidden error
   */
  get isForbidden(): boolean {
    return this.status === 403;
  }

  /**
   * Returns true if this is a 404 Not Found error
   */
  get isNotFound(): boolean {
    return this.status === 404;
  }

  /**
   * Returns true if this is a 400 Bad Request error
   */
  get isBadRequest(): boolean {
    return this.status === 400;
  }

  /**
   * Returns true if this is a 422 Validation error
   */
  get isValidationError(): boolean {
    return this.status === 422;
  }

  /**
   * Returns true if this is a 5xx server error
   */
  get isServerError(): boolean {
    return this.status >= 500;
  }

  /**
   * Returns true if this is a network/connection error (status 0)
   */
  get isNetworkError(): boolean {
    return this.status === 0;
  }

  /**
   * Returns true if this is a timeout error
   */
  get isTimeout(): boolean {
    return this.code === 'TIMEOUT';
  }
}

/**
 * Type guard to check if an error is an ApiError
 * Works with both instanceof checks and duck typing
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError || (error as ApiError)?.isApiError === true;
}
