# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# Load environment variables from .env file
from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = os.path.join(BASE_DIR, '.env')

# Load environment variables from .env file if it exists
if os.path.exists(env_path):
    load_dotenv(env_path)

__all__ = ('celery_app',)

