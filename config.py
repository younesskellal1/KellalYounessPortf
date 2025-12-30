"""
Configuration file for the Portfolio Application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Secret key for session management (change in production)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production-2024')

# SQLite database path
DATABASE_PATH = BASE_DIR / 'portfolio.db'

# JSON database path (kept for backward compatibility, but data is now in SQLite)
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

# Admin credentials are now stored in the database
# Environment variables are used only for initial setup/migration
# Optionally load a .env file if python-dotenv is installed
try:
	from dotenv import load_dotenv  # type: ignore
	_DOTENV_AVAILABLE = True
except Exception:
	_DOTENV_AVAILABLE = False

if _DOTENV_AVAILABLE:
	# load .env located at BASE_DIR/.env if present
	load_dotenv(dotenv_path=BASE_DIR / '.env')

# Admin credentials are stored and handled in the database.
# No ADMIN_USERNAME/ADMIN_PASSWORD fallback from environment variables is used.

# Maximum file size (16MB)
MAX_CONTENT_LENGTH = 16 * 1024 * 1024


