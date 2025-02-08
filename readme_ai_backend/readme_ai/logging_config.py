import logging
from readme_ai.settings import get_settings

settings = get_settings()


logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)
