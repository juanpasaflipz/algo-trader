const API_BASE_URL = '/api/v1';

interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

class ApiService {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: data.detail || 'An error occurred',
          status: response.status,
        };
      }

      return {
        data,
        status: response.status,
      };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : 'Network error',
        status: 0,
      };
    }
  }

  // Health check
  async health() {
    return this.request('/health');
  }

  // Trading endpoints
  async getPositions() {
    return this.request('/positions');
  }

  async getOrders() {
    return this.request('/orders');
  }

  async getTrades(limit = 10) {
    return this.request(`/trades?limit=${limit}`);
  }

  async getAccountBalance() {
    return this.request('/account/balance');
  }

  // Strategy endpoints
  async getStrategies() {
    return this.request('/strategies');
  }

  async toggleStrategy(strategyId: string, enabled: boolean) {
    return this.request(`/strategies/${strategyId}`, {
      method: 'PATCH',
      body: JSON.stringify({ enabled }),
    });
  }

  async getStrategyPerformance(strategyId: string) {
    return this.request(`/strategies/${strategyId}/performance`);
  }

  // Backtest endpoints
  async runBacktest(params: {
    strategy: string;
    startDate: string;
    endDate: string;
    symbol: string;
    timeframe: string;
  }) {
    return this.request('/tasks/backtest', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  async getBacktestResult(taskId: string) {
    return this.request(`/tasks/${taskId}`);
  }

  // WebSocket connection for real-time updates
  connectWebSocket(onMessage: (data: any) => void) {
    const ws = new WebSocket(`ws://localhost:8000/ws`);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      // Reconnect after 5 seconds
      setTimeout(() => this.connectWebSocket(onMessage), 5000);
    };

    return ws;
  }
}

export const api = new ApiService();