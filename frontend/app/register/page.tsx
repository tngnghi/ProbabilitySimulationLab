/*Purpose: Create new account

Form Fields:


Email (text input)
Password (password input)
Confirm Password (password input)


Validation (before submit):


Email looks valid (basic regex or HTML5)
Password >= 8 characters
Passwords match
Show error message if not


On Submit:

1. Call apiCall('POST /auth/register', {
     email: email,
     password: password
   })

2. If success (201):
     - Show "Account created" message
     - Redirect to /login

3. If error (400 or 422):
     - Display error message to user
     - Don't redirect

Error Handling:

409 Conflict → "Email already registered"
422 Unprocessable → "Invalid input (email/password)"
500 Server Error → "Server error, try again later"*/