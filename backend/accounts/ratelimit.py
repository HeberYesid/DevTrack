"""
Rate limiting decorators and utilities for API endpoints.

This module provides reusable rate limiting configurations to protect
against brute force attacks, abuse, and excessive API usage.
"""
from functools import wraps
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from django_ratelimit.exceptions import Ratelimited


def ratelimit_handler(request, exception):
    """
    Custom handler for rate limit exceeded responses.
    Returns a JSON response with appropriate status code.
    """
    return JsonResponse({
        'detail': 'Demasiados intentos. Por favor, espera un momento antes de intentar nuevamente.',
        'error': 'rate_limit_exceeded'
    }, status=429)


def apply_ratelimit(key='ip', rate='5/m', method='POST', block=True):
    """
    Wrapper decorator that applies rate limiting and handles exceptions.
    
    Args:
        key: What to rate limit on ('ip', 'user', or callable)
        rate: Rate limit string (e.g., '5/m' = 5 per minute, '10/h' = 10 per hour)
        method: HTTP methods to rate limit ('POST', 'GET', 'ALL')
        block: Whether to block requests that exceed the limit
    
    Usage:
        @apply_ratelimit(rate='5/m')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @ratelimit(key=key, rate=rate, method=method, block=block)
        def wrapped_view(request, *args, **kwargs):
            # Check if the request was rate limited
            was_limited = getattr(request, 'limited', False)
            if was_limited:
                return ratelimit_handler(request, None)
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# Pre-configured decorators for common use cases

def ratelimit_auth(view_func):
    """
    Rate limit for authentication endpoints (login, register).
    5 attempts per minute per IP.
    """
    return apply_ratelimit(key='ip', rate='5/m', method='POST', block=True)(view_func)


def ratelimit_strict_auth(view_func):
    """
    Strict rate limit for sensitive auth operations.
    3 attempts per minute per IP.
    """
    return apply_ratelimit(key='ip', rate='3/m', method='POST', block=True)(view_func)


def ratelimit_email(view_func):
    """
    Rate limit for email-related operations (verification, resend).
    3 attempts per 5 minutes per IP.
    """
    return apply_ratelimit(key='ip', rate='3/5m', method='POST', block=True)(view_func)


def ratelimit_api_read(view_func):
    """
    Rate limit for read operations.
    100 requests per minute per user.
    """
    return apply_ratelimit(key='user_or_ip', rate='100/m', method='GET', block=True)(view_func)


def ratelimit_api_write(view_func):
    """
    Rate limit for write operations.
    30 requests per minute per user.
    """
    return apply_ratelimit(key='user_or_ip', rate='30/m', method=['POST', 'PUT', 'PATCH', 'DELETE'], block=True)(view_func)


def ratelimit_upload(view_func):
    """
    Rate limit for file upload operations.
    5 uploads per minute per user.
    """
    return apply_ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True)(view_func)
