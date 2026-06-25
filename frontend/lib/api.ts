
/*Create fetch wrapper that:
  1. Reads token from localStorage
  2. Adds Authorization header
  3. Makes request to backend
  4. If 401: call clearToken() + redirect to /login
  5. Return response JSON

Function: apiCall(endpoint, options) -> Promise
  - Wraps fetch()
  - Handles auth, errors, JSON parsing*/

async function apiCall(endpoint, options):Promise {
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
    router.push('/login')
  }
  
  return response.json()
}