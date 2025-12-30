"""
SQLite database module for portfolio data storage
"""
import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from contextlib import contextmanager

class Database:
    """SQLite database handler for portfolio data"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Personal info table (single row)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS personal_info (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT,
                    title TEXT,
                    email TEXT,
                    phone TEXT,
                    location TEXT,
                    bio TEXT,
                    github TEXT,
                    linkedin TEXT,
                    twitter TEXT,
                    profile_image TEXT,
                    cv_file TEXT
                )
            ''')
            
            # Academic table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS academic (
                    id TEXT PRIMARY KEY,
                    degree TEXT,
                    institution TEXT,
                    year TEXT,
                    description TEXT
                )
            ''')
            
            # Work Experience table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS work_experience (
                    id TEXT PRIMARY KEY,
                    job_title TEXT,
                    company TEXT,
                    location TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    current INTEGER DEFAULT 0,
                    description TEXT,
                    responsibilities TEXT,
                    achievements TEXT,
                    technologies TEXT
                )
            ''')
            
            # Projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    technologies TEXT,  -- JSON array
                    github_url TEXT,
                    live_url TEXT,
                    image_url TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    featured INTEGER DEFAULT 0
                )
            ''')
            
            # Project screenshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_screenshots (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    filename TEXT,
                    caption TEXT,
                    uploaded_at TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            ''')
            
            # Skills table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS skills (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    level INTEGER,
                    category TEXT,
                    icon TEXT,
                    description TEXT
                )
            ''')
            
            # Certifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS certifications (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    issuer TEXT,
                    date TEXT,
                    credential_id TEXT,
                    credential_url TEXT,
                    expiry_date TEXT,
                    description TEXT
                )
            ''')
            
            # Messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    subject TEXT,
                    message TEXT,
                    date TEXT,
                    read INTEGER DEFAULT 0
                )
            ''')
            
            # Articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    slug TEXT UNIQUE,
                    excerpt TEXT,
                    content TEXT,
                    image_url TEXT,
                    categories TEXT,  -- JSON array
                    tags TEXT,  -- JSON array
                    published_date TEXT,
                    read_time TEXT,
                    published INTEGER DEFAULT 0
                )
            ''')
            
            # Testimonials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS testimonials (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    role TEXT,
                    company TEXT,
                    content TEXT,
                    rating INTEGER,
                    image_url TEXT,
                    date TEXT,
                    featured INTEGER DEFAULT 0
                )
            ''')
            
            # Analytics tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_page_views (
                    route TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_section_views (
                    section TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_daily_views (
                    date TEXT PRIMARY KEY,
                    count INTEGER DEFAULT 0
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_unique_visitors (
                    visitor_id TEXT PRIMARY KEY
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_visitor_sessions (
                    visitor_id TEXT PRIMARY KEY,
                    first_visit TEXT,
                    last_visit TEXT,
                    total_visits INTEGER DEFAULT 0,
                    pages_visited TEXT  -- JSON array
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Admin users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_login TEXT,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Initialize personal_info with default values if empty
            cursor.execute('SELECT COUNT(*) FROM personal_info')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO personal_info (id, name, title, email, phone, location, bio, 
                                             github, linkedin, twitter, profile_image, cv_file)
                    VALUES (1, 'Your Name', 'Full-Stack Developer', 'your.email@example.com',
                           '+1 (555) 000-0000', 'City, Country', 
                           'A passionate developer creating innovative solutions.',
                           'https://github.com/yourusername',
                           'https://linkedin.com/in/yourusername',
                           'https://twitter.com/yourusername',
                           '/static/images/profile.jpg', NULL)
                ''')
            
            # Initialize analytics metadata
            cursor.execute('SELECT COUNT(*) FROM analytics_metadata WHERE key = ?', ('total_views',))
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO analytics_metadata (key, value)
                    VALUES ('total_views', '0'), ('last_reset', NULL)
                ''')
            
            # Initialize admin_users table (already created above)
    
    # ==================== PORTFOLIO DATA METHODS ====================
    
    def load_portfolio_data(self) -> Dict[str, Any]:
        """Load all portfolio data from database"""
        data = {
            "personal_info": {
                "name": "",
                "title": "",
                "email": "",
                "phone": "",
                "location": "",
                "bio": "",
                "social_links": {
                    "github": "",
                    "linkedin": "",
                    "twitter": ""
                },
                "profile_image": "/static/images/profile.jpg"
            },
            "academic": [],
            "work_experience": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "cv_file": None,
            "messages": [],
            "articles": [],
            "testimonials": []
        }
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Load personal info
            cursor.execute('SELECT * FROM personal_info WHERE id = 1')
            row = cursor.fetchone()
            if row:
                data["personal_info"] = {
                    "name": row["name"] or "",
                    "title": row["title"] or "",
                    "email": row["email"] or "",
                    "phone": row["phone"] or "",
                    "location": row["location"] or "",
                    "bio": row["bio"] or "",
                    "social_links": {
                        "github": row["github"] or "",
                        "linkedin": row["linkedin"] or "",
                        "twitter": row["twitter"] or ""
                    },
                    "profile_image": row["profile_image"] or "/static/images/profile.jpg"
                }
                data["cv_file"] = row["cv_file"]
            
            # Load academic
            cursor.execute('SELECT * FROM academic ORDER BY year DESC')
            for row in cursor.fetchall():
                data["academic"].append({
                    "id": row["id"],
                    "degree": row["degree"],
                    "institution": row["institution"],
                    "year": row["year"],
                    "description": row["description"] or ""
                })
            
            # Load work experience
            cursor.execute('SELECT * FROM work_experience ORDER BY start_date DESC, end_date DESC')
            for row in cursor.fetchall():
                data["work_experience"].append({
                    "id": row["id"],
                    "job_title": row["job_title"],
                    "company": row["company"],
                    "location": row["location"] or "",
                    "start_date": row["start_date"] or "",
                    "end_date": row["end_date"] or "",
                    "current": bool(row["current"]),
                    "description": row["description"] or "",
                    "responsibilities": json.loads(row["responsibilities"] or "[]"),
                    "achievements": json.loads(row["achievements"] or "[]"),
                    "technologies": json.loads(row["technologies"] or "[]")
                })
            
            # Load projects
            cursor.execute('SELECT * FROM projects')
            for row in cursor.fetchall():
                project = {
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "technologies": json.loads(row["technologies"] or "[]"),
                    "github_url": row["github_url"] or "",
                    "live_url": row["live_url"] or "",
                    "image_url": row["image_url"] or "",
                    "start_date": row["start_date"] or "",
                    "end_date": row["end_date"] or "",
                    "featured": bool(row["featured"]),
                    "screenshots": []
                }
                
                # Load screenshots for this project
                cursor.execute('SELECT * FROM project_screenshots WHERE project_id = ?', (row["id"],))
                for screenshot in cursor.fetchall():
                    project["screenshots"].append({
                        "id": screenshot["id"],
                        "filename": screenshot["filename"],
                        "caption": screenshot["caption"] or "",
                        "uploaded_at": screenshot["uploaded_at"] or ""
                    })
                
                data["projects"].append(project)
            
            # Load skills
            cursor.execute('SELECT * FROM skills')
            for row in cursor.fetchall():
                data["skills"].append({
                    "id": row["id"],
                    "name": row["name"],
                    "level": row["level"],
                    "category": row["category"],
                    "icon": row["icon"] or "",
                    "description": row["description"] or ""
                })
            
            # Load certifications
            cursor.execute('SELECT * FROM certifications')
            for row in cursor.fetchall():
                data["certifications"].append({
                    "id": row["id"],
                    "name": row["name"],
                    "issuer": row["issuer"],
                    "date": row["date"],
                    "credential_id": row["credential_id"] or "",
                    "credential_url": row["credential_url"] or "",
                    "expiry_date": row["expiry_date"] or "",
                    "description": row["description"] or ""
                })
            
            # Load messages
            cursor.execute('SELECT * FROM messages ORDER BY date DESC')
            for row in cursor.fetchall():
                data["messages"].append({
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "subject": row["subject"],
                    "message": row["message"],
                    "date": row["date"],
                    "read": bool(row["read"])
                })
            
            # Load articles
            cursor.execute('SELECT * FROM articles ORDER BY published_date DESC')
            for row in cursor.fetchall():
                data["articles"].append({
                    "id": row["id"],
                    "title": row["title"],
                    "slug": row["slug"],
                    "excerpt": row["excerpt"] or "",
                    "content": row["content"],
                    "image_url": row["image_url"] or "",
                    "categories": json.loads(row["categories"] or "[]"),
                    "tags": json.loads(row["tags"] or "[]"),
                    "published_date": row["published_date"] or "",
                    "read_time": row["read_time"] or "",
                    "published": bool(row["published"])
                })
            
            # Load testimonials
            cursor.execute('SELECT * FROM testimonials ORDER BY date DESC')
            for row in cursor.fetchall():
                data["testimonials"].append({
                    "id": row["id"],
                    "name": row["name"],
                    "role": row["role"] or "",
                    "company": row["company"] or "",
                    "content": row["content"],
                    "rating": row["rating"],
                    "image_url": row["image_url"] or "",
                    "date": row["date"],
                    "featured": bool(row["featured"])
                })
        
        return data
    
    def save_personal_info(self, personal_info: Dict[str, Any], cv_file: Optional[str] = None):
        """Save personal information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            social_links = personal_info.get("social_links", {})
            cursor.execute('''
                UPDATE personal_info SET
                    name = ?, title = ?, email = ?, phone = ?, location = ?, bio = ?,
                    github = ?, linkedin = ?, twitter = ?, profile_image = ?, cv_file = ?
                WHERE id = 1
            ''', (
                personal_info.get("name", ""),
                personal_info.get("title", ""),
                personal_info.get("email", ""),
                personal_info.get("phone", ""),
                personal_info.get("location", ""),
                personal_info.get("bio", ""),
                social_links.get("github", ""),
                social_links.get("linkedin", ""),
                social_links.get("twitter", ""),
                personal_info.get("profile_image", "/static/images/profile.jpg"),
                cv_file
            ))
    
    def add_academic(self, entry: Dict[str, Any]):
        """Add academic entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO academic (id, degree, institution, year, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                entry["id"],
                entry.get("degree", ""),
                entry.get("institution", ""),
                entry.get("year", ""),
                entry.get("description", "")
            ))
    
    def update_academic(self, entry_id: str, entry: Dict[str, Any]):
        """Update academic entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE academic SET
                    degree = ?, institution = ?, year = ?, description = ?
                WHERE id = ?
            ''', (
                entry.get("degree", ""),
                entry.get("institution", ""),
                entry.get("year", ""),
                entry.get("description", ""),
                entry_id
            ))
    
    def delete_academic(self, entry_id: str):
        """Delete academic entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM academic WHERE id = ?', (entry_id,))
    
    def add_work_experience(self, entry: Dict[str, Any]):
        """Add work experience entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO work_experience (id, job_title, company, location, start_date, end_date, 
                                           current, description, responsibilities, achievements, technologies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry["id"],
                entry.get("job_title", ""),
                entry.get("company", ""),
                entry.get("location", ""),
                entry.get("start_date", ""),
                entry.get("end_date", ""),
                1 if entry.get("current", False) else 0,
                entry.get("description", ""),
                json.dumps(entry.get("responsibilities", [])),
                json.dumps(entry.get("achievements", [])),
                json.dumps(entry.get("technologies", []))
            ))
    
    def update_work_experience(self, entry_id: str, entry: Dict[str, Any]):
        """Update work experience entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE work_experience SET
                    job_title = ?, company = ?, location = ?, start_date = ?, end_date = ?,
                    current = ?, description = ?, responsibilities = ?, achievements = ?, technologies = ?
                WHERE id = ?
            ''', (
                entry.get("job_title", ""),
                entry.get("company", ""),
                entry.get("location", ""),
                entry.get("start_date", ""),
                entry.get("end_date", ""),
                1 if entry.get("current", False) else 0,
                entry.get("description", ""),
                json.dumps(entry.get("responsibilities", [])),
                json.dumps(entry.get("achievements", [])),
                json.dumps(entry.get("technologies", [])),
                entry_id
            ))
    
    def delete_work_experience(self, entry_id: str):
        """Delete work experience entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM work_experience WHERE id = ?', (entry_id,))
    
    def add_project(self, project: Dict[str, Any]):
        """Add project"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO projects (id, title, description, technologies, github_url, live_url,
                                    image_url, start_date, end_date, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project["id"],
                project.get("title", ""),
                project.get("description", ""),
                json.dumps(project.get("technologies", [])),
                project.get("github_url", ""),
                project.get("live_url", ""),
                project.get("image_url", ""),
                project.get("start_date", ""),
                project.get("end_date", ""),
                1 if project.get("featured", False) else 0
            ))
            
            # Add screenshots if any
            for screenshot in project.get("screenshots", []):
                cursor.execute('''
                    INSERT INTO project_screenshots (id, project_id, filename, caption, uploaded_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    screenshot.get("id", ""),
                    project["id"],
                    screenshot.get("filename", ""),
                    screenshot.get("caption", ""),
                    screenshot.get("uploaded_at", "")
                ))
    
    def update_project(self, project_id: str, project: Dict[str, Any]):
        """Update project"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects SET
                    title = ?, description = ?, technologies = ?, github_url = ?, live_url = ?,
                    image_url = ?, start_date = ?, end_date = ?, featured = ?
                WHERE id = ?
            ''', (
                project.get("title", ""),
                project.get("description", ""),
                json.dumps(project.get("technologies", [])),
                project.get("github_url", ""),
                project.get("live_url", ""),
                project.get("image_url", ""),
                project.get("start_date", ""),
                project.get("end_date", ""),
                1 if project.get("featured", False) else 0,
                project_id
            ))
    
    def delete_project(self, project_id: str):
        """Delete project (cascades to screenshots)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    
    def add_project_screenshot(self, project_id: str, screenshot: Dict[str, Any]):
        """Add project screenshot"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO project_screenshots (id, project_id, filename, caption, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                screenshot.get("id", ""),
                project_id,
                screenshot.get("filename", ""),
                screenshot.get("caption", ""),
                screenshot.get("uploaded_at", "")
            ))
    
    def delete_project_screenshot(self, screenshot_id: str):
        """Delete project screenshot"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM project_screenshots WHERE id = ?', (screenshot_id,))
    
    def add_skill(self, skill: Dict[str, Any]):
        """Add skill"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO skills (id, name, level, category, icon, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                skill["id"],
                skill.get("name", ""),
                skill.get("level", 0),
                skill.get("category", ""),
                skill.get("icon", ""),
                skill.get("description", "")
            ))
    
    def update_skill(self, skill_id: str, skill: Dict[str, Any]):
        """Update skill"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE skills SET
                    name = ?, level = ?, category = ?, icon = ?, description = ?
                WHERE id = ?
            ''', (
                skill.get("name", ""),
                skill.get("level", 0),
                skill.get("category", ""),
                skill.get("icon", ""),
                skill.get("description", ""),
                skill_id
            ))
    
    def delete_skill(self, skill_id: str):
        """Delete skill"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    
    def add_certification(self, certification: Dict[str, Any]):
        """Add certification"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO certifications (id, name, issuer, date, credential_id, credential_url, expiry_date, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                certification["id"],
                certification.get("name", ""),
                certification.get("issuer", ""),
                certification.get("date", ""),
                certification.get("credential_id", ""),
                certification.get("credential_url", ""),
                certification.get("expiry_date", ""),
                certification.get("description", "")
            ))
    
    def update_certification(self, cert_id: str, certification: Dict[str, Any]):
        """Update certification"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE certifications SET
                    name = ?, issuer = ?, date = ?, credential_id = ?, credential_url = ?, expiry_date = ?, description = ?
                WHERE id = ?
            ''', (
                certification.get("name", ""),
                certification.get("issuer", ""),
                certification.get("date", ""),
                certification.get("credential_id", ""),
                certification.get("credential_url", ""),
                certification.get("expiry_date", ""),
                certification.get("description", ""),
                cert_id
            ))
    
    def delete_certification(self, cert_id: str):
        """Delete certification"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM certifications WHERE id = ?', (cert_id,))
    
    def add_message(self, message: Dict[str, Any]):
        """Add message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (id, name, email, subject, message, date, read)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message["id"],
                message.get("name", ""),
                message.get("email", ""),
                message.get("subject", ""),
                message.get("message", ""),
                message.get("date", ""),
                1 if message.get("read", False) else 0
            ))
    
    def update_message(self, message_id: str, message: Dict[str, Any]):
        """Update message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages SET
                    name = ?, email = ?, subject = ?, message = ?, date = ?, read = ?
                WHERE id = ?
            ''', (
                message.get("name", ""),
                message.get("email", ""),
                message.get("subject", ""),
                message.get("message", ""),
                message.get("date", ""),
                1 if message.get("read", False) else 0,
                message_id
            ))
    
    def delete_message(self, message_id: str):
        """Delete message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
    
    def add_article(self, article: Dict[str, Any]):
        """Add article"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO articles (id, title, slug, excerpt, content, image_url, categories, tags,
                                    published_date, read_time, published)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article["id"],
                article.get("title", ""),
                article.get("slug", ""),
                article.get("excerpt", ""),
                article.get("content", ""),
                article.get("image_url", ""),
                json.dumps(article.get("categories", [])),
                json.dumps(article.get("tags", [])),
                article.get("published_date", ""),
                article.get("read_time", ""),
                1 if article.get("published", False) else 0
            ))
    
    def update_article(self, article_id: str, article: Dict[str, Any]):
        """Update article"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE articles SET
                    title = ?, slug = ?, excerpt = ?, content = ?, image_url = ?, categories = ?,
                    tags = ?, published_date = ?, read_time = ?, published = ?
                WHERE id = ?
            ''', (
                article.get("title", ""),
                article.get("slug", ""),
                article.get("excerpt", ""),
                article.get("content", ""),
                article.get("image_url", ""),
                json.dumps(article.get("categories", [])),
                json.dumps(article.get("tags", [])),
                article.get("published_date", ""),
                article.get("read_time", ""),
                1 if article.get("published", False) else 0,
                article_id
            ))
    
    def delete_article(self, article_id: str):
        """Delete article"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM articles WHERE id = ?', (article_id,))
    
    def add_testimonial(self, testimonial: Dict[str, Any]):
        """Add testimonial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO testimonials (id, name, role, company, content, rating, image_url, date, featured)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                testimonial["id"],
                testimonial.get("name", ""),
                testimonial.get("role", ""),
                testimonial.get("company", ""),
                testimonial.get("content", ""),
                testimonial.get("rating", 5),
                testimonial.get("image_url", ""),
                testimonial.get("date", ""),
                1 if testimonial.get("featured", False) else 0
            ))
    
    def update_testimonial(self, testimonial_id: str, testimonial: Dict[str, Any]):
        """Update testimonial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE testimonials SET
                    name = ?, role = ?, company = ?, content = ?, rating = ?, image_url = ?, date = ?, featured = ?
                WHERE id = ?
            ''', (
                testimonial.get("name", ""),
                testimonial.get("role", ""),
                testimonial.get("company", ""),
                testimonial.get("content", ""),
                testimonial.get("rating", 5),
                testimonial.get("image_url", ""),
                testimonial.get("date", ""),
                1 if testimonial.get("featured", False) else 0,
                testimonial_id
            ))
    
    def delete_testimonial(self, testimonial_id: str):
        """Delete testimonial"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM testimonials WHERE id = ?', (testimonial_id,))
    
    # ==================== ANALYTICS METHODS ====================
    
    def load_analytics_data(self) -> Dict[str, Any]:
        """Load analytics data from database"""
        data = {
            "page_views": {},
            "section_views": {},
            "daily_views": {},
            "unique_visitors": [],
            "visitor_sessions": {},
            "total_views": 0,
            "last_reset": None
        }
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Load page views
            cursor.execute('SELECT route, count FROM analytics_page_views')
            for row in cursor.fetchall():
                data["page_views"][row["route"]] = row["count"]
            
            # Load section views
            cursor.execute('SELECT section, count FROM analytics_section_views')
            for row in cursor.fetchall():
                data["section_views"][row["section"]] = row["count"]
            
            # Load daily views
            cursor.execute('SELECT date, count FROM analytics_daily_views')
            for row in cursor.fetchall():
                data["daily_views"][row["date"]] = row["count"]
            
            # Load unique visitors
            cursor.execute('SELECT visitor_id FROM analytics_unique_visitors')
            data["unique_visitors"] = [row["visitor_id"] for row in cursor.fetchall()]
            
            # Load visitor sessions
            cursor.execute('SELECT * FROM analytics_visitor_sessions')
            for row in cursor.fetchall():
                data["visitor_sessions"][row["visitor_id"]] = {
                    "first_visit": row["first_visit"],
                    "last_visit": row["last_visit"],
                    "total_visits": row["total_visits"],
                    "pages_visited": json.loads(row["pages_visited"] or "[]")
                }
            
            # Load metadata
            cursor.execute('SELECT value FROM analytics_metadata WHERE key = ?', ('total_views',))
            row = cursor.fetchone()
            if row:
                data["total_views"] = int(row["value"] or 0)
            
            cursor.execute('SELECT value FROM analytics_metadata WHERE key = ?', ('last_reset',))
            row = cursor.fetchone()
            if row:
                data["last_reset"] = row["value"]
        
        return data
    
    def track_page_view(self, route: str, visitor_id: Optional[str] = None):
        """Track a page view"""
        today = date.today().isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Track page views
            cursor.execute('''
                INSERT INTO analytics_page_views (route, count)
                VALUES (?, 1)
                ON CONFLICT(route) DO UPDATE SET count = count + 1
            ''', (route,))
            
            # Track daily views
            cursor.execute('''
                INSERT INTO analytics_daily_views (date, count)
                VALUES (?, 1)
                ON CONFLICT(date) DO UPDATE SET count = count + 1
            ''', (today,))
            
            # Track unique visitors
            if visitor_id:
                cursor.execute('''
                    INSERT OR IGNORE INTO analytics_unique_visitors (visitor_id)
                    VALUES (?)
                ''', (visitor_id,))
            
            # Track visitor sessions
            if visitor_id:
                cursor.execute('SELECT * FROM analytics_visitor_sessions WHERE visitor_id = ?', (visitor_id,))
                session_row = cursor.fetchone()
                
                if session_row:
                    pages_visited = json.loads(session_row["pages_visited"] or "[]")
                    if route not in pages_visited:
                        pages_visited.append(route)
                    
                    cursor.execute('''
                        UPDATE analytics_visitor_sessions SET
                            last_visit = ?, total_visits = total_visits + 1, pages_visited = ?
                        WHERE visitor_id = ?
                    ''', (today, json.dumps(pages_visited), visitor_id))
                else:
                    cursor.execute('''
                        INSERT INTO analytics_visitor_sessions (visitor_id, first_visit, last_visit, total_visits, pages_visited)
                        VALUES (?, ?, ?, 1, ?)
                    ''', (visitor_id, today, today, json.dumps([route])))
            
            # Increment total views
            cursor.execute('''
                UPDATE analytics_metadata SET value = CAST(value AS INTEGER) + 1
                WHERE key = 'total_views'
            ''')
    
    def track_section_view(self, section: str):
        """Track a section view"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analytics_section_views (section, count)
                VALUES (?, 1)
                ON CONFLICT(section) DO UPDATE SET count = count + 1
            ''', (section,))
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for dashboard"""
        data = self.load_analytics_data()
        
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
    
    def reset_analytics(self):
        """Reset all analytics data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM analytics_page_views')
            cursor.execute('DELETE FROM analytics_section_views')
            cursor.execute('DELETE FROM analytics_daily_views')
            cursor.execute('DELETE FROM analytics_unique_visitors')
            cursor.execute('DELETE FROM analytics_visitor_sessions')
            cursor.execute('UPDATE analytics_metadata SET value = ? WHERE key = ?', ('0', 'total_views'))
            cursor.execute('UPDATE analytics_metadata SET value = ? WHERE key = ?', (datetime.now().isoformat(), 'last_reset'))
    
    def export_portfolio_data(self, export_path: Path) -> bool:
        """Export portfolio data to JSON file"""
        try:
            data = self.load_portfolio_data()
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting portfolio data: {e}")
            return False
    
    def import_portfolio_data(self, import_path: Path) -> bool:
        """Import portfolio data from JSON file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Clear existing data
                cursor.execute('DELETE FROM academic')
                cursor.execute('DELETE FROM work_experience')
                cursor.execute('DELETE FROM projects')
                cursor.execute('DELETE FROM project_screenshots')
                cursor.execute('DELETE FROM skills')
                cursor.execute('DELETE FROM certifications')
                cursor.execute('DELETE FROM messages')
                cursor.execute('DELETE FROM articles')
                cursor.execute('DELETE FROM testimonials')
                
                # Import personal info
                if "personal_info" in data:
                    self.save_personal_info(data["personal_info"], data.get("cv_file"))
                
                # Import academic
                for entry in data.get("academic", []):
                    self.add_academic(entry)
                
                # Import work experience
                for entry in data.get("work_experience", []):
                    self.add_work_experience(entry)
                
                # Import projects
                for project in data.get("projects", []):
                    self.add_project(project)
                
                # Import skills
                for skill in data.get("skills", []):
                    self.add_skill(skill)
                
                # Import certifications
                for cert in data.get("certifications", []):
                    self.add_certification(cert)
                
                # Import messages
                for msg in data.get("messages", []):
                    self.add_message(msg)
                
                # Import articles
                for article in data.get("articles", []):
                    self.add_article(article)
                
                # Import testimonials
                for testimonial in data.get("testimonials", []):
                    self.add_testimonial(testimonial)
            
            return True
        except Exception as e:
            print(f"Error importing portfolio data: {e}")
            return False
    
    # ==================== DATABASE EXPLORER METHODS ====================
    
    def get_tables(self) -> List[str]:
        """Get list of all tables in the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row[0] for row in cursor.fetchall()]
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table"""
        # Validate table name (prevent SQL injection)
        if not table_name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid table name")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Use parameterized query where possible, but PRAGMA doesn't support it
            # So we validate the table name first
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': bool(row[3]),
                    'default_value': row[4],
                    'pk': bool(row[5])
                })
            return columns
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get number of rows in a table"""
        # Validate table name (prevent SQL injection)
        if not table_name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid table name")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
    
    def get_table_data(self, table_name: str, limit: int = 100, offset: int = 0, order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get data from a table with pagination"""
        # Validate table name (prevent SQL injection)
        if not table_name.replace('_', '').replace('-', '').isalnum():
            raise ValueError("Invalid table name")
        
        # Validate order_by if provided
        if order_by and not order_by.replace('_', '').replace('-', '').replace(' ', '').replace(',', '').isalnum():
            raise ValueError("Invalid order_by parameter")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query
            query = f"SELECT * FROM {table_name}"
            if order_by:
                query += f" ORDER BY {order_by}"
            query += f" LIMIT {limit} OFFSET {offset}"
            
            cursor.execute(query)
            rows = []
            for row in cursor.fetchall():
                row_dict = {}
                for key in row.keys():
                    value = row[key]
                    # Convert JSON strings to objects for display
                    if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                        try:
                            value = json.loads(value)
                        except:
                            pass
                    row_dict[key] = value
                rows.append(row_dict)
            return rows
    
    def execute_readonly_query(self, query: str, limit: int = 1000) -> Dict[str, Any]:
        """Execute a read-only SQL query (SELECT only)"""
        # Security: Only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed")
        
        # Prevent dangerous operations
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'EXEC', 'EXECUTE']
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Add limit if not present
            if 'LIMIT' not in query_upper:
                query = f"{query.rstrip(';')} LIMIT {limit}"
            
            try:
                cursor.execute(query)
                columns = [description[0] for description in cursor.description] if cursor.description else []
                rows = []
                for row in cursor.fetchall():
                    row_dict = {}
                    for i, key in enumerate(columns):
                        value = row[i]
                        # Convert JSON strings to objects for display
                        if isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                            try:
                                value = json.loads(value)
                            except:
                                pass
                        row_dict[key] = value
                    rows.append(row_dict)
                
                return {
                    'columns': columns,
                    'rows': rows,
                    'row_count': len(rows)
                }
            except Exception as e:
                raise ValueError(f"Query error: {str(e)}")
    
    def get_table_info(self) -> List[Dict[str, Any]]:
        """Get information about all tables"""
        tables = self.get_tables()
        table_info = []
        for table in tables:
            table_info.append({
                'name': table,
                'row_count': self.get_table_row_count(table),
                'columns': len(self.get_table_schema(table))
            })
        return table_info
    
    # ==================== ADMIN CREDENTIALS METHODS ====================
    
    def hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_admin_credentials(self, username: str, password: str) -> bool:
        """Verify admin username and password"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id FROM admin_users 
                WHERE username = ? AND password_hash = ? AND is_active = 1
            ''', (username, password_hash))
            return cursor.fetchone() is not None
    
    def get_admin_credentials(self) -> Optional[Dict[str, str]]:
        """Get admin credentials from database (for backward compatibility)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT username, password_hash FROM admin_users WHERE is_active = 1 LIMIT 1')
            row = cursor.fetchone()
            if row:
                return {
                    'username': row['username'],
                    'password_hash': row['password_hash']
                }
            return None
    
    def create_admin_user(self, username: str, password: str) -> bool:
        """Create a new admin user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                password_hash = self.hash_password(password)
                cursor.execute('''
                    INSERT INTO admin_users (username, password_hash)
                    VALUES (?, ?)
                ''', (username, password_hash))
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
        except Exception as e:
            print(f"Error creating admin user: {e}")
            return False
    
    def update_admin_password(self, username: str, new_password: str) -> bool:
        """Update admin user password"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                password_hash = self.hash_password(new_password)
                cursor.execute('''
                    UPDATE admin_users 
                    SET password_hash = ?
                    WHERE username = ? AND is_active = 1
                ''', (password_hash, username))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating admin password: {e}")
            return False
    
    def update_admin_username(self, old_username: str, new_username: str) -> bool:
        """Update admin username"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE admin_users 
                    SET username = ?
                    WHERE username = ? AND is_active = 1
                ''', (new_username, old_username))
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            # New username already exists
            return False
        except Exception as e:
            print(f"Error updating admin username: {e}")
            return False
    
    def record_admin_login(self, username: str) -> None:
        """Record admin login timestamp"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE admin_users 
                    SET last_login = ?
                    WHERE username = ?
                ''', (datetime.now().isoformat(), username))
        except Exception as e:
            print(f"Error recording admin login: {e}")
    
    def initialize_admin_from_env(self, username: str, password: str) -> bool:
        """Initialize admin user from environment variables (migration helper)"""
        # Check if admin user already exists
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM admin_users')
            if cursor.fetchone()[0] > 0:
                return False  # Admin already exists
        
        # Create admin user
        return self.create_admin_user(username, password)

