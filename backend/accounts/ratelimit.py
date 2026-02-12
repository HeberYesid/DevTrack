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
    """
    from django_ratelimit.core import is_ratelimited

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            # Find request object in args
            request = None
            for arg in args:
                if hasattr(arg, 'META') and hasattr(arg, 'method'):
                    request = arg
                    break
            
            # If we found a request, apply rate limiting manually
            if request:
                # Determine group name (default to path or func name)
                # We use a fixed group or None to let ratelimit decide based on key/view
                group_name = getattr(view_func, '__qualname__', getattr(view_func, '__name__', str(view_func)))
                if hasattr(view_func, '__module__'):
                    group_name = f"{view_func.__module__}.{group_name}"

                # Check limit
                # Note: is_ratelimited returns True if limited
                is_limited = is_ratelimited(
                    request, 
                    group=group_name, 
                    key=key, 
                    rate=rate, 
                    method=method, 
                    increment=True
                )
                
                if is_limited and block:
                    return ratelimit_handler(request, None)
            
            return view_func(*args, **kwargs)
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
