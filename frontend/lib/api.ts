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