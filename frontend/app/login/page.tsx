/*Purpose: Authenticate user

Form Fields:


Email (text input)
Password (password input)
"Remember me" checkbox (optional, not required)


On Submit:

1. Call apiCall('POST /auth/login', {
     email: email,
     password: password
   })

2. If success (200):
     - Save token: setToken(response.access_token)
     - Redirect to /dashboard

3. If error (401):
     - Display "Invalid email or password"
     - Don't redirect*/