import ApiError from "./apierror";

interface RequestOptions {
  method?: string;
  headers?: Record<string, string>;
  timeout?: number;
  body?: string;
  // Add more options as needed
}

class DataFetcher {
  private baseURL: string;
  private headers: Record<string, string>;

  constructor(baseURL: string, headers: Record<string, string> = {}) {
    this.baseURL = baseURL;
    this.headers = headers;
  }

  async fetchData<T>(
    endpoint: string,
    options: RequestOptions = {},
  ): Promise<T> {
    const url = `${this.baseURL}/${endpoint}`;
    const { timeout = 8000, ...restOptions } = options;

    try {
      const response = await this.fetchWithTimeout(url, {
        ...restOptions,
        headers: {
          Accept: "application/json",
          ...this.headers,
          ...restOptions.headers,
        },
        timeout,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(error);
      throw error;
    }
  }

  async get<T>(
    endpoint: string,
    additionalHeaders: Record<string, string> = {},
  ): Promise<T> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      const response = await this.fetchWithTimeout(url, {
        method: "GET",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")} `,
          ...additionalHeaders,
        },
      });

      if (response.error) {
        throw new Error(`${response?.error?.message}`);
      }

      return await response;
    } catch (error) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  async postImage<T>(
    endpoint: string,
    data: any = {},
    additionalHeaders: Record<string, string> = {},
  ): Promise<T> {
    const url = `${this.baseURL}/${endpoint}`;
    const formDataPresent = data instanceof FormData;

    try {
      const response = await this.fetchWithTimeout(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          ...additionalHeaders,
        },
        body: formDataPresent ? data : JSON.stringify(data),
      });

      if (response.error) {
        throw new Error(`${response?.error?.message}`);
      }

      return await response;
    } catch (error: any) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  async post<T>(
    endpoint: string,
    data: any = {},
    additionalHeaders: Record<string, string> = {},
  ): Promise<T> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      const response = await this.fetchWithTimeout(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          ...additionalHeaders,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.error) {
        throw new Error(`${response?.error?.message}`);
      }

      return await response;
    } catch (error: any) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  async put<T>(
    endpoint: string,
    data: any = {},
    additionalHeaders: Record<string, string> = {},
  ): Promise<T> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      const response = await this.fetchWithTimeout(url, {
        method: "PUT",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          ...additionalHeaders,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.error) {
        throw new Error(`${response?.error?.message}`);
      }

      return await response;
    } catch (error) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  async delete<T>(
    endpoint: string,
    additionalHeaders: Record<string, string> = {},
  ): Promise<T | void> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      await this.fetchWithTimeout(url, {
        method: "DELETE",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          ...additionalHeaders,
        },
      });

      return;
    } catch (error) {
      console.error(error);
      if (error?.name === "AbortError") {
        throw new Error("Poor internet connection.");
      }
      throw error;
    }
  }

  async patch<T>(
    endpoint: string,
    data: any = {},
    additionalHeaders: Record<string, string> = {},
  ): Promise<T> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      const response = await this.fetchWithTimeout(url, {
        method: "PATCH",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")}`,
          ...additionalHeaders,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (response.error) {
        throw new Error(`${response?.error?.message}`);
      }

      return await response;
    } catch (error) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  async getText(
    endpoint: string,
    additionalHeaders: Record<string, string> = {},
  ): Promise<string> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")} `,
          ...additionalHeaders,
        },
      });

      return await response.text();
    } catch (error) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  async getBlob(
    endpoint: string,
    additionalHeaders: Record<string, string> = {},
  ): Promise<Blob> {
    const url = `${this.baseURL}/${endpoint}`;

    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          Accept: "application/json",
          ...this.headers,
          Authorization: `Bearer ${localStorage.getItem("token")} `,
          ...additionalHeaders,
        },
      });

      return await response.blob();
    } catch (error) {
      console.error(error);
      if (error?.name === "AbortError")
        throw new Error("Poor internet connection.");
      throw error;
    }
  }

  private async fetchWithTimeout(resource: string, options: RequestOptions) {
    const { timeout = 8000 } = options;

    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(resource, {
        ...options,
        signal: controller.signal,
      });

      if (!response.ok) {
        const res = await response.json();
        throw new ApiError(res.status, res.message, res.error);
      }

      if (response.status === 204) {
        return;
      }

      return response.json();
    } finally {
      clearTimeout(id);
    }
  }
}

// Create an instance of DataFetcher with your base URL and headers
const api = new DataFetcher(
  import.meta.env.VITE_APP_ENV === "dev"
    ? import.meta.env.VITE_API_DEV_URL
    : import.meta.env.VITE_API_PROD_URL,
  {
    Accept: "application/json",
    Authorization: `Bearer ${localStorage.getItem("token")}`,
  },
);

export default api;
