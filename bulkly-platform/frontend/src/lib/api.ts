const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
  requireAuth?: boolean;
}

export async function fetchApi<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { requireAuth = true, headers: customHeaders, ...rest } = options;

  const headers = new Headers(customHeaders);
  headers.set("Content-Type", "application/json");

  if (requireAuth) {
    const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    } else {
      // Handle missing token (e.g., redirect to login)
      console.warn("No auth token found for secure request");
    }
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    headers,
    ...rest,
  });

  if (!response.ok) {
    if (response.status === 401 && typeof window !== 'undefined') {
        localStorage.removeItem("token");
        window.location.href = "/login";
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API request failed with status ${response.status}`);
  }

  // Some endpoints (like DELETE) might return 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
