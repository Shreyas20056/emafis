const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getStoredToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("emafis_token");
  }
  return null;
}

export function setStoredToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem("emafis_token", token);
  }
}

export function removeStoredToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("emafis_token");
    localStorage.removeItem("emafis_user");
  }
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data.detail || data.message || `API Error (${response.status})`;
    throw new Error(errorMsg);
  }

  return data as T;
}

// Auth API Calls
export async function signupApi(name: string, email: string, password: string): Promise<{ token: string; user: any }> {
  return apiRequest("/api/auth/signup", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

export async function loginApi(email: string, password: string): Promise<{ token: string; user: any }> {
  return apiRequest("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getMeApi(): Promise<{ user: any }> {
  return apiRequest("/api/auth/me");
}

// Stock Analysis API Calls
export async function analyzeStockApi(ticker: string) {
  return apiRequest(`/api/analyze/${encodeURIComponent(ticker)}`, {
    method: "POST",
  });
}

export async function getChartDataApi(ticker: string, period: string = "3mo") {
  return apiRequest(`/api/chart/${encodeURIComponent(ticker)}?period=${period}`);
}

export async function getLatestAnalysisApi(ticker: string) {
  return apiRequest(`/api/analyze/${encodeURIComponent(ticker)}/latest`);
}

export async function getRecommendationsHistoryApi(limit: number = 20) {
  return apiRequest(`/api/recommendations/history?limit=${limit}`);
}

// Portfolio API Calls
export async function getPortfolioApi() {
  return apiRequest("/api/portfolio");
}

export async function addHoldingApi(holding: { ticker: string; quantity: number; avg_buy_price: number; buy_date?: string }) {
  return apiRequest("/api/portfolio/holdings", {
    method: "POST",
    body: JSON.stringify(holding),
  });
}

export async function updateHoldingApi(ticker: string, data: { quantity?: number; avg_buy_price?: number; buy_date?: string }) {
  return apiRequest(`/api/portfolio/holdings/${encodeURIComponent(ticker)}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteHoldingApi(ticker: string) {
  return apiRequest(`/api/portfolio/holdings/${encodeURIComponent(ticker)}`, {
    method: "DELETE",
  });
}

export async function recordTradeApi(trade: { ticker: string; action: "BUY" | "SELL"; quantity: number; price: number; date?: string }) {
  return apiRequest("/api/portfolio/trade", {
    method: "POST",
    body: JSON.stringify(trade),
  });
}

export async function analyzePortfolioApi() {
  return apiRequest("/api/portfolio/analyze", {
    method: "POST",
  });
}

export async function chatPortfolioApi(message: string, history: any[] = []) {
  return apiRequest("/api/portfolio/chat", {
    method: "POST",
    body: JSON.stringify({ message, history }),
  });
}

export async function getAgentPerformanceApi() {
  return apiRequest("/api/agent-performance");
}
