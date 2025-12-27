"""
Configuration file for the Portfolio Application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Secret key for session management (change in production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-2024')

# JSON database path
PORTFOLIO_DATA_PATH = BASE_DIR / 'portfolio_data.json'
ANALYTICS_DATA_PATH = BASE_DIR / 'analytics_data.json'

# File upload configuration
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
CV_UPLOAD_FOLDER = UPLOAD_FOLDER / 'cv'
PROJECT_SCREENSHOTS_FOLDER = UPLOAD_FOLDER / 'project_screenshots'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

# Ensure upload directories exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
CV_UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
PROJECT_SCREENSHOTS_FOLDER.mkdir(parents=True, exist_ok=True)

# Admin credentials (must be set via environment variables)
# For security, we do NOT provide defaults here. Set these in your OS
# environment or use a local `.env` file (only for development) and ensure
# it is excluded from version control.

# Optionally load a .env file if python-dotenv is installed. This is
# convenient for local development but NOT recommended for production.
try:
	from dotenv import load_dotenv  # type: ignore
	_DOTENV_AVAILABLE = True
except Exception:
	_DOTENV_AVAILABLE = False

if _DOTENV_AVAILABLE:
	# load .env located at BASE_DIR/.env if present
	load_dotenv(dotenv_path=BASE_DIR / '.env')

ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Trim whitespace if someone accidentally includes it when setting env vars
if isinstance(ADMIN_USERNAME, str):
	ADMIN_USERNAME = ADMIN_USERNAME.strip()
if isinstance(ADMIN_PASSWORD, str):
	ADMIN_PASSWORD = ADMIN_PASSWORD.strip()

# Fail fast if credentials are missing — this enforces secret management
if not ADMIN_USERNAME or not ADMIN_PASSWORD:
	raise RuntimeError(
		'ADMIN_USERNAME and ADMIN_PASSWORD environment variables must be set. '
		'For local development you can create a .env file in the project root ' 
		'with ADMIN_USERNAME and ADMIN_PASSWORD, and make sure it is NOT committed.'
	)

# Maximum file size (16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024


