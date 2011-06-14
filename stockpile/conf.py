from django.conf import settings

# Logging
import logging
log = logging.getLogger(__name__)

# Testing and Debug settings
TESTING = getattr(settings, 'STOCKPILE_TESTING', False)
DEBUG = getattr(settings, 'DEBUG', False) and not TESTING
