"""
Utility functions for SQLite database operations and file handling
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
import shutil
from datetime import datetime, date
from collections import defaultdict
from database import Database

# Global database instance (initialized on first use)
_db_instance = None

def get_db() -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        from config import DATABASE_PATH
        _db_instance = Database(DATABASE_PATH)
    return _db_instance

def load_portfolio_data(file_path: Path = None) -> Dict[str, Any]:
    """Load portfolio data from SQLite database"""
    try:
        db = get_db()
        return db.load_portfolio_data()
    except Exception as e:
        print(f"Error loading portfolio data: {e}")
        return {
            "personal_info": {},
            "academic": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "cv_file": None,
            "messages": [],
            "articles": [],
            "testimonials": []
        }

def save_portfolio_data(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save portfolio data to SQLite database"""
    try:
        db = get_db()
        
        # Save personal info
        if "personal_info" in data:
            db.save_personal_info(data["personal_info"], data.get("cv_file"))
        
        # Note: Individual CRUD operations should be used for adding/updating/deleting items
        # This function is kept for compatibility but should ideally use specific methods
        return True
    except Exception as e:
        print(f"Error saving portfolio data: {e}")
        return False

def get_item_by_id(items: List[Dict], item_id: str) -> Optional[Dict]:
    """Get an item by its ID from a list"""
    return next((item for item in items if item.get('id') == item_id), None)

def generate_id() -> str:
    """Generate a unique ID"""
    import time
    return str(int(time.time() * 1000))

def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text"""
    import re
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_cv_file(file, upload_folder: Path) -> Optional[str]:
    """Save uploaded CV file and return the filename"""
    if file and allowed_file(file.filename, {'pdf', 'doc', 'docx'}):
        filename = secure_filename(file.filename)
        # Ensure unique filename
        file_path = upload_folder / filename
        counter = 1
        while file_path.exists():
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            file_path = upload_folder / filename
            counter += 1
        
        file.save(str(file_path))
        return filename
    return None

def save_screenshot(file, upload_folder: Path) -> Optional[str]:
    """Save uploaded screenshot image and return the filename"""
    if file and allowed_file(file.filename, {'jpg', 'jpeg', 'png', 'gif', 'webp'}):
        filename = secure_filename(file.filename)
        # Ensure unique filename
        file_path = upload_folder / filename
        counter = 1
        while file_path.exists():
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{counter}{ext}"
            file_path = upload_folder / filename
            counter += 1
        
        file.save(str(file_path))
        return filename
    return None

def delete_screenshot(filename: str, upload_folder: Path) -> bool:
    """Delete screenshot file"""
    if filename:
        file_path = upload_folder / filename
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                print(f"Error deleting screenshot: {e}")
                return False
    return False

def delete_cv_file(filename: str, upload_folder: Path) -> bool:
    """Delete CV file"""
    if filename:
        file_path = upload_folder / filename
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                print(f"Error deleting CV file: {e}")
                return False
    return False

def export_portfolio_data(file_path: Path, export_path: Path) -> bool:
    """Export portfolio data to a backup file"""
    try:
        db = get_db()
        return db.export_portfolio_data(export_path)
    except Exception as e:
        print(f"Error exporting portfolio data: {e}")
        return False

def import_portfolio_data(file_path: Path, import_path: Path) -> bool:
    """Import portfolio data from a backup file"""
    try:
        db = get_db()
        return db.import_portfolio_data(import_path)
    except Exception as e:
        print(f"Error importing portfolio data: {e}")
        return False

# ==================== ANALYTICS FUNCTIONS ====================

def load_analytics_data(file_path: Path = None) -> Dict[str, Any]:
    """Load analytics data from SQLite database"""
    try:
        db = get_db()
        return db.load_analytics_data()
    except Exception as e:
        print(f"Error loading analytics data: {e}")
        return {
            "page_views": {},
            "section_views": {},
            "daily_views": {},
            "unique_visitors": [],
            "visitor_sessions": {},
            "total_views": 0,
            "last_reset": None
        }

def save_analytics_data(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save analytics data (kept for compatibility, but analytics are tracked directly)"""
    # Analytics are now tracked directly in the database, this function is kept for compatibility
    return True

def track_page_view(file_path: Path, route: str, visitor_id: str = None) -> None:
    """Track a page view"""
    try:
        db = get_db()
        db.track_page_view(route, visitor_id)
    except Exception as e:
        print(f"Error tracking page view: {e}")

def track_section_view(file_path: Path, section: str) -> None:
    """Track a section view (e.g., skills, projects, etc.)"""
    try:
        db = get_db()
        db.track_section_view(section)
    except Exception as e:
        print(f"Error tracking section view: {e}")

def get_analytics_summary(file_path: Path = None) -> Dict[str, Any]:
    """Get analytics summary for dashboard"""
    try:
        db = get_db()
        return db.get_analytics_summary()
    except Exception as e:
        print(f"Error getting analytics summary: {e}")
        return {
            'total_views': 0,
            'unique_visitors': 0,
            'top_pages': [],
            'top_sections': [],
            'daily_views': [],
            'avg_daily_views': 0,
            'visitor_sessions': 0
        }

def reset_analytics(file_path: Path = None) -> bool:
    """Reset all analytics data"""
    try:
        db = get_db()
        db.reset_analytics()
        return True
    except Exception as e:
        print(f"Error resetting analytics: {e}")
        return False

