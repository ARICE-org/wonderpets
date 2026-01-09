import { useEffect, useState, useCallback } from 'react';
import { soilForecastService } from '../lib/api/services/soil-forecast.service';
import { isApiError } from '../lib/api';
import type { SoilForecastResponse } from '../lib/api/services/soil-forecast.types';

interface UseSoilForecastState {
  data: SoilForecastResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch and manage soil forecast data
 * @param farmerId - The farmer's unique identifier
 * @param autoFetch - Whether to automatically fetch on mount (default: true)
 * @returns Object containing forecast data, loading state, error, and refetch function
 *
 * @example
 * const { data, loading, error, refetch } = useSoilForecast('farmer-id-123');
 * 
 * if (loading) return <Text>Loading...</Text>;
 * if (error) return <Text>Error: {error}</Text>;
 * 
 * return (
 *   <View>
 *     <Text>Health Score: {data?.currentHealthScore}</Text>
 *   </View>
 * );
 */
export function useSoilForecast(
  farmerId: string,
  autoFetch = true
): UseSoilForecastState {
  const [data, setData] = useState<SoilForecastResponse | null>(null);
  const [loading, setLoading] = useState(autoFetch);
  const [error, setError] = useState<string | null>(null);

  const fetchForecast = useCallback(async () => {
    if (!farmerId) {
      setError('Farmer ID is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const response = await soilForecastService.getForecast(farmerId);
      setData(response);
    } catch (err) {
      if (isApiError(err)) {
        if (err.isUnauthorized) {
          setError('Session expired. Please log in again.');
        } else if (err.isNotFound) {
          setError('No forecast data found for this farmer.');
        } else if (err.isNetworkError) {
          setError('Network error. Please check your connection.');
        } else if (err.isTimeout) {
          setError('Request timed out. Please try again.');
        } else {
          setError(err.message);
        }
      } else {
        setError(err instanceof Error ? err.message : 'An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  }, [farmerId]);

  useEffect(() => {
    if (autoFetch) {
      fetchForecast();
    }
  }, [farmerId, autoFetch, fetchForecast]);

  const refetch = useCallback(async () => {
    await fetchForecast();
  }, [fetchForecast]);

  return { data, loading, error, refetch };
}

export default useSoilForecast;
