import { useState, useEffect } from 'react';
import { api } from '../services/api';

export function useApiData<T>(
  fetcher: () => Promise<{ data?: T; error?: string }>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetcher();
        
        if (!cancelled) {
          if (response.error) {
            setError(response.error);
          } else {
            setData(response.data || null);
            setError(null);
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'An error occurred');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, dependencies);

  return { data, loading, error, refetch: () => {} };
}

export function useWebSocket(onMessage: (data: any) => void) {
  useEffect(() => {
    const ws = api.connectWebSocket(onMessage);
    
    return () => {
      ws.close();
    };
  }, [onMessage]);
}