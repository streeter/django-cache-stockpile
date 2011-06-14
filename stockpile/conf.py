from django.conf import settings

# Testing and Debug settings
TESTING = getattr(settings, 'STOCKPILE_TESTING', False)
DEBUG = getattr(settings, 'DEBUG', False) and not TESTING

# Caching Enabled
ENABLED = True

# Cache Prefix
PREFIX = getattr(settings, 'CACHE_PREFIX', '')

# Cache Timeouts
TIMEOUT_DEFAULT = getattr(settings, 'CACHE_TIMEOUT', 60)
TIMEOUT_INFINITY = 0
TIMEOUT_NO_CACHE = -1
