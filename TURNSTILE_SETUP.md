# Cloudflare Turnstile Integration

This document explains how to set up and use Cloudflare Turnstile in the DevTrack application.

## Overview

Cloudflare Turnstile has been integrated into both the login and registration forms to provide bot protection and enhance security.

## Setup Instructions

### 1. Environment Variables

#### Backend (.env)
Add the following to your backend `.env` file:
```
TURNSTILE_SECRET_KEY=0x4AAAAAAB195dF8QdRbAuGMD3aVvy8Q_V4
```

#### Frontend (.env)
Add the following to your frontend `.env` file:
```
VITE_TURNSTILE_SITE_KEY=0x4AAAAAAB195XyO5y089iC-
```

### 2. Install Dependencies

Make sure to install the new backend dependency:
```bash
cd backend
pip install -r requirements.txt
```

### 3. How It Works

#### Frontend
- The `TurnstileCaptcha` component renders the Cloudflare Turnstile widget
- Users must complete the captcha before submitting login/registration forms
- The component handles token generation, errors, and expiration

#### Backend
- The `verify_turnstile_token()` function validates tokens with Cloudflare's API
- Both login and registration serializers require and validate turnstile tokens
- Invalid tokens result in authentication/validation errors

## Components

### TurnstileCaptcha.jsx
A reusable React component that:
- Loads the Turnstile script dynamically
- Renders the captcha widget
- Handles callbacks for verification, errors, and expiration
- Provides reset functionality

### Backend Integration
- `accounts/utils.py`: Contains the `verify_turnstile_token()` function
- `accounts/serializers.py`: Updated to include turnstile token validation
- `accounts/views.py`: Updated to pass request context to serializers

## Usage

The Turnstile captcha is automatically included in:
- Login form (`/login`)
- Registration form (`/register`)

Users must complete the captcha verification before they can submit these forms.

## Security Features

1. **Token Validation**: All tokens are verified server-side with Cloudflare
2. **IP Validation**: Client IP is included in verification requests
3. **Single Use**: Tokens are consumed after verification
4. **Expiration**: Tokens have built-in expiration handling
5. **Error Handling**: Graceful degradation on network errors

## Development Mode

In development mode with `DEBUG=True`, if no `TURNSTILE_SECRET_KEY` is provided, the verification will be skipped to allow for easier testing.

## Troubleshooting

### Common Issues

1. **"Cargando captcha..." stuck**: 
   - Check that the Turnstile script is loading properly
   - Verify the site key is correct

2. **"Verificación de seguridad fallida"**:
   - Check that the secret key is correct in backend .env
   - Verify network connectivity to Cloudflare

3. **Captcha not appearing**:
   - Ensure the Turnstile script is included in index.html
   - Check browser console for JavaScript errors

### Testing

To test the implementation:
1. Try submitting forms without completing the captcha
2. Complete the captcha and submit the form
3. Test with invalid/expired tokens

## API Changes

### Login Endpoint
```json
POST /api/auth/login/
{
  "email": "user@example.com",
  "password": "password123",
  "turnstile_token": "token_from_captcha"
}
```

### Register Endpoint
```json
POST /api/auth/register/
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "turnstile_token": "token_from_captcha"
}
```

## Security Considerations

1. Keep your secret key secure and never expose it in frontend code
2. The site key can be public but should be environment-specific
3. Consider implementing rate limiting for additional protection
4. Monitor Turnstile analytics in your Cloudflare dashboard

## Production Deployment

Before deploying to production:
1. Update environment variables with production keys
2. Test the integration thoroughly
3. Monitor error rates and user experience
4. Consider implementing fallback mechanisms for high-availability scenarios
