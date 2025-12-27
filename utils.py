"""
Utility functions for JSON CRUD operations and file handling
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from werkzeug.utils import secure_filename
import shutil
from datetime import datetime, date
from collections import defaultdict

def load_portfolio_data(file_path: Path) -> Dict[str, Any]:
    """Load portfolio data from JSON file"""
    if not file_path.exists():
        # Initialize with default structure
        default_data = {
            "personal_info": {
                "name": "Your Name",
                "title": "Full-Stack Developer",
                "email": "your.email@example.com",
                "phone": "+1 (555) 000-0000",
                "location": "City, Country",
                "bio": "A passionate developer creating innovative solutions.",
                "social_links": {
                    "github": "https://github.com/yourusername",
                    "linkedin": "https://linkedin.com/in/yourusername",
                    "twitter": "https://twitter.com/yourusername"
                },
                "profile_image": "/static/images/profile.jpg"
            },
            "academic": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "cv_file": None,
            "messages": [],
            "articles": [],
            "testimonials": []
        }
        save_portfolio_data(file_path, default_data)
        return default_data
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading portfolio data: {e}")
        return {}

def save_portfolio_data(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save portfolio data to JSON file atomically"""
    try:
        # Write to temporary file first
        temp_path = file_path.with_suffix('.json.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic replace
        if os.name == 'nt':  # Windows
            if file_path.exists():
                os.replace(temp_path, file_path)
            else:
                temp_path.rename(file_path)
        else:  # Unix-like
            os.replace(temp_path, file_path)
        
        return True
    except Exception as e:
        print(f"Error saving portfolio data: {e}")
        if temp_path.exists():
            temp_path.unlink()
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
        data = load_portfolio_data(file_path)
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error exporting portfolio data: {e}")
        return False

def import_portfolio_data(file_path: Path, import_path: Path) -> bool:
    """Import portfolio data from a backup file"""
    try:
        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return save_portfolio_data(file_path, data)
    except Exception as e:
        print(f"Error importing portfolio data: {e}")
        return False

# ==================== ANALYTICS FUNCTIONS ====================

def load_analytics_data(file_path: Path) -> Dict[str, Any]:
    """Load analytics data from JSON file"""
    if not file_path.exists():
        default_data = {
            "page_views": {},
            "section_views": {},
            "daily_views": {},
            "unique_visitors": [],
            "visitor_sessions": {},
            "total_views": 0,
            "last_reset": None
        }
        save_analytics_data(file_path, default_data)
        return default_data
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
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
    """Save analytics data to JSON file atomically"""
    try:
        # Create backup
        if file_path.exists():
            backup_path = file_path.with_suffix('.json.bak')
            shutil.copy2(file_path, backup_path)
        
        # Write to temporary file first
        temp_path = file_path.with_suffix('.json.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic move
        if os.name == 'nt':  # Windows
            if file_path.exists():
                os.replace(temp_path, file_path)
            else:
                temp_path.rename(file_path)
        else:  # Unix-like
            os.replace(temp_path, file_path)
        
        # Remove backup if successful
        backup_path = file_path.with_suffix('.json.bak')
        if backup_path.exists():
            backup_path.unlink()
        
        return True
    except Exception as e:
        print(f"Error saving analytics data: {e}")
        # Restore from backup if available
        backup_path = file_path.with_suffix('.json.bak')
        if backup_path.exists():
            try:
                if os.name == 'nt':
                    os.replace(backup_path, file_path)
                else:
                    backup_path.replace(file_path)
            except:
                pass
        return False

def track_page_view(file_path: Path, route: str, visitor_id: str = None) -> None:
    """Track a page view"""
    data = load_analytics_data(file_path)
    today = date.today().isoformat()
    
    # Track page views
    if route not in data['page_views']:
        data['page_views'][route] = 0
    data['page_views'][route] += 1
    
    # Track daily views
    if today not in data['daily_views']:
        data['daily_views'][today] = 0
    data['daily_views'][today] += 1
    
    # Track unique visitors
    if visitor_id and visitor_id not in data['unique_visitors']:
        data['unique_visitors'].append(visitor_id)
    
    # Track visitor sessions
    if visitor_id:
        if visitor_id not in data['visitor_sessions']:
            data['visitor_sessions'][visitor_id] = {
                'first_visit': today,
                'last_visit': today,
                'total_visits': 0,
                'pages_visited': []
            }
        data['visitor_sessions'][visitor_id]['last_visit'] = today
        data['visitor_sessions'][visitor_id]['total_visits'] += 1
        if route not in data['visitor_sessions'][visitor_id]['pages_visited']:
            data['visitor_sessions'][visitor_id]['pages_visited'].append(route)
    
    # Increment total views
    data['total_views'] += 1
    
    save_analytics_data(file_path, data)

def track_section_view(file_path: Path, section: str) -> None:
    """Track a section view (e.g., skills, projects, etc.)"""
    data = load_analytics_data(file_path)
    
    if section not in data['section_views']:
        data['section_views'][section] = 0
    data['section_views'][section] += 1
    
    save_analytics_data(file_path, data)

def get_analytics_summary(file_path: Path) -> Dict[str, Any]:
    """Get analytics summary for dashboard"""
    data = load_analytics_data(file_path)
    
    # Get top pages
    top_pages = sorted(
        data['page_views'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Get top sections
    top_sections = sorted(
        data['section_views'].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    # Get daily views for last 30 days
    daily_views_list = sorted(
        data['daily_views'].items(),
        key=lambda x: x[0],
        reverse=True
    )[:30]
    
    # Calculate unique visitors count
    unique_visitors_count = len(data['unique_visitors'])
    
    # Calculate average views per day (last 30 days)
    recent_days = daily_views_list[:30]
    avg_daily_views = sum(views for _, views in recent_days) / len(recent_days) if recent_days else 0
    
    return {
        'total_views': data['total_views'],
        'unique_visitors': unique_visitors_count,
        'top_pages': top_pages,
        'top_sections': top_sections,
        'daily_views': daily_views_list,
        'avg_daily_views': round(avg_daily_views, 2),
        'visitor_sessions': len(data['visitor_sessions'])
    }

def reset_analytics(file_path: Path) -> bool:
    """Reset all analytics data"""
    default_data = {
        "page_views": {},
        "section_views": {},
        "daily_views": {},
        "unique_visitors": [],
        "visitor_sessions": {},
        "total_views": 0,
        "last_reset": datetime.now().isoformat()
    }
    return save_analytics_data(file_path, default_data)

