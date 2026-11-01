// Base API Client utilizing native fetch for clean zero-dependency requests
const API_BASE = '/api';

export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  details?: any;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<{ data: ApiResponse<T>; status: number }> {
    const url = `${API_BASE}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
    
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string>),
    };

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include', // send session cookies
      });

      const json = await response.json().catch(() => ({
        success: false,
        error: response.statusText || 'Server Error'
      }));

      if (!response.ok) {
        const errorMsg = json.error || 'Unable to process your request. Please try again.';
        const err = new Error(errorMsg);
        (err as any).response = { data: json, status: response.status };
        throw err;
      }

      return { data: json, status: response.status };
    } catch (err: any) {
      if (err.response) throw err;
      const networkError = new Error('Unable to connect to ANIKA-AI backend. Please ensure the server is running.');
      (networkError as any).response = {
        data: { success: false, error: networkError.message },
        status: 503
      };
      throw networkError;
    }
  }

  get<T = any>(endpoint: string, headers?: Record<string, string>) {
    return this.request<T>(endpoint, { method: 'GET', headers });
  }

  post<T = any>(endpoint: string, body?: any, headers?: Record<string, string>) {
    const isFormData = body instanceof FormData;
    return this.request<T>(endpoint, {
      method: 'POST',
      body: isFormData ? body : JSON.stringify(body || {}),
      headers,
    });
  }

  delete<T = any>(endpoint: string, headers?: Record<string, string>) {
    return this.request<T>(endpoint, { method: 'DELETE', headers });
  }
}

export const api = new ApiClient();
