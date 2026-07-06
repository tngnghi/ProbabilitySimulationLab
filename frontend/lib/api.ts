import { getToken, clearToken } from './auth';
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'


export async function apiCall<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  }
  
  const response = await fetch(API_URL + endpoint, {
    ...options,
    headers
  })
  
  if (response.status === 401) {
    clearToken()
    if (typeof window !== 'undefined') {
      window.location.assign('/login');
    }
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json()
}
/*// lib/api.ts (simple fetch wrapper)
export async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: any = { ...options.headers };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    clearToken();
    window.location.href = '/login'; // force full redirect
    throw new Error('Session expired. Please log in again.');
  }

  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}*/