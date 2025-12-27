"""
Main Flask application for Portfolio Website
"""
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, jsonify
from pathlib import Path
import os
from config import (
    SECRET_KEY, PORTFOLIO_DATA_PATH, CV_UPLOAD_FOLDER,
    PROJECT_SCREENSHOTS_FOLDER, ADMIN_USERNAME, ADMIN_PASSWORD,
    ALLOWED_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS, ANALYTICS_DATA_PATH
)
from utils import (
    load_portfolio_data, save_portfolio_data, get_item_by_id,
    generate_id, save_cv_file, delete_cv_file, export_portfolio_data,
    import_portfolio_data, allowed_file, save_screenshot, delete_screenshot,
    load_analytics_data, track_page_view, track_section_view, get_analytics_summary, reset_analytics,
    generate_slug
)
from i18n import (
    get_current_language, set_language, get_translation,
    get_translations_for_language, update_translation,
    load_translations, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
)

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# ==================== ANALYTICS MIDDLEWARE ====================
@app.before_request
def track_analytics():
    """Track page views before each request"""
    # Skip tracking for admin routes, static files, and API endpoints
    if request.path.startswith('/admin') or \
       request.path.startswith('/static') or \
       request.path.startswith('/api') or \
       request.path.startswith('/set-language'):
        return
    
    # Get visitor ID from session or use IP address
    if 'visitor_id' not in session:
        import uuid
        session['visitor_id'] = str(uuid.uuid4())
    
    visitor_id = session.get('visitor_id')
    
    # Track page view
    route = request.path
    track_page_view(ANALYTICS_DATA_PATH, route, visitor_id)
    
    # Track section views based on route
    if route == '/skills':
        track_section_view(ANALYTICS_DATA_PATH, 'skills')
    elif route == '/projects':
        track_section_view(ANALYTICS_DATA_PATH, 'projects')
    elif route == '/education':
        track_section_view(ANALYTICS_DATA_PATH, 'education')
    elif route == '/certifications':
        track_section_view(ANALYTICS_DATA_PATH, 'certifications')
    elif route == '/about':
        track_section_view(ANALYTICS_DATA_PATH, 'about')
    elif route == '/contact':
        track_section_view(ANALYTICS_DATA_PATH, 'contact')
    elif route == '/':
        track_section_view(ANALYTICS_DATA_PATH, 'home')
    elif route.startswith('/projects/'):
        track_section_view(ANALYTICS_DATA_PATH, 'project_detail')
    elif route == '/blog' or route.startswith('/blog/'):
        track_section_view(ANALYTICS_DATA_PATH, 'blog')

# ==================== I18N CONTEXT PROCESSOR ====================
@app.context_processor
def inject_language():
    """Inject language and translation function into all templates"""
    current_lang = get_current_language()
    return {
        'current_language': current_lang,
        'supported_languages': SUPPORTED_LANGUAGES,
        't': get_translation,
        'lang': current_lang
    }

# ==================== LANGUAGE ROUTES ====================
@app.route('/set-language/<language>')
def set_language_route(language):
    """Set language and redirect back"""
    set_language(language)
    return redirect(request.referrer or url_for('index'))

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    """Home page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    # Detect language from browser if not set
    if 'language' not in session:
        browser_lang = request.accept_languages.best_match(['en', 'fr', 'ar'])
        set_language(browser_lang or DEFAULT_LANGUAGE)
    return render_template('index.html', data=data)

@app.route('/projects')
def projects():
    """Projects page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('projects.html', data=data)

@app.route('/projects/<project_id>')
def project_detail(project_id):
    """Project detail page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    projects = data.get('projects', [])
    project = get_item_by_id(projects, project_id)
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('projects'))
    
    return render_template('project_detail.html', data=data, project=project)

@app.route('/about')
def about():
    """About page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('about.html', data=data)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        # Validate
        if not all([name, email, subject, message]):
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('contact'))
        
        # Create message entry
        from datetime import datetime
        new_message = {
            'id': generate_id(),
            'name': name,
            'email': email,
            'subject': subject,
            'message': message,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'read': False
        }
        
        # Add to messages
        if 'messages' not in data:
            data['messages'] = []
        data['messages'].append(new_message)
        
        # Save
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Thank you for your message! I will get back to you soon.', 'success')
        else:
            flash('Error sending message. Please try again.', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html', data=data)

@app.route('/skills')
def skills():
    """Skills page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('skills.html', data=data)

@app.route('/certifications')
def certifications():
    """Certifications page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('certifications.html', data=data)

@app.route('/education')
def education():
    """Education page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('education.html', data=data)

@app.route('/blog')
def blog():
    """Blog listing page"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    articles = data.get('articles', [])
    # Only show published articles
    articles = [a for a in articles if a.get('published', False)]
    
    # Get query parameters
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    tag = request.args.get('tag', '').strip()
    
    # Filter articles
    filtered_articles = articles
    if search_query:
        filtered_articles = [
            article for article in filtered_articles
            if search_query.lower() in article.get('title', '').lower() or
               search_query.lower() in article.get('content', '').lower() or
               search_query.lower() in article.get('excerpt', '').lower()
        ]
    if category:
        filtered_articles = [
            article for article in filtered_articles
            if category.lower() in [c.lower() for c in article.get('categories', [])]
        ]
    if tag:
        filtered_articles = [
            article for article in filtered_articles
            if tag.lower() in [t.lower() for t in article.get('tags', [])]
        ]
    
    # Sort by date (newest first)
    filtered_articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
    
    # Get all categories and tags for filters
    all_categories = set()
    all_tags = set()
    for article in articles:
        all_categories.update(article.get('categories', []))
        all_tags.update(article.get('tags', []))
    
    return render_template('blog.html', data=data, articles=filtered_articles,
                         all_articles=articles, search_query=search_query,
                         category=category, tag=tag, all_categories=sorted(all_categories),
                         all_tags=sorted(all_tags))

@app.route('/blog/<slug>')
def blog_post(slug):
    """Individual blog post page (SEO-friendly URL)"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    articles = data.get('articles', [])
    article = next((a for a in articles if a.get('slug') == slug), None)
    
    if not article:
        flash('Article not found.', 'error')
        return redirect(url_for('blog'))
    
    # Get related articles (same category or tags)
    related_articles = [
        a for a in articles
        if a.get('id') != article.get('id') and (
            set(a.get('categories', [])) & set(article.get('categories', [])) or
            set(a.get('tags', [])) & set(article.get('tags', []))
        )
    ][:3]
    
    return render_template('blog_post.html', data=data, article=article, related_articles=related_articles)

@app.route('/download-cv')
def download_cv():
    """Download CV file"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    cv_file = data.get('cv_file')
    
    if cv_file and (CV_UPLOAD_FOLDER / cv_file).exists():
        return send_from_directory(
            str(CV_UPLOAD_FOLDER),
            cv_file,
            as_attachment=True
        )
    flash('CV file not found.', 'error')
    return redirect(url_for('index'))

@app.route('/api/portfolio-data')
def api_portfolio_data():
    """API endpoint to get portfolio data for chat assistant"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return jsonify(data)

# ==================== ADMIN ROUTES ====================

def admin_required(f):
    """Decorator to require admin authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'error')
    
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    analytics_summary = get_analytics_summary(ANALYTICS_DATA_PATH)
    return render_template('admin/dashboard.html', data=data, analytics_summary=analytics_summary)

# ==================== ADMIN CRUD - PERSONAL INFO ====================

@app.route('/admin/personal-info', methods=['GET', 'POST'])
@admin_required
def admin_personal_info():
    """Update personal information"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    
    if request.method == 'POST':
        personal_info = data.get('personal_info', {})
        personal_info['name'] = request.form.get('name', '')
        personal_info['title'] = request.form.get('title', '')
        personal_info['email'] = request.form.get('email', '')
        personal_info['phone'] = request.form.get('phone', '')
        personal_info['location'] = request.form.get('location', '')
        personal_info['bio'] = request.form.get('bio', '')
        personal_info['social_links'] = {
            'github': request.form.get('github', ''),
            'linkedin': request.form.get('linkedin', ''),
            'twitter': request.form.get('twitter', '')
        }
        
        data['personal_info'] = personal_info
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Personal information updated successfully!', 'success')
        else:
            flash('Error updating personal information.', 'error')
        
        return redirect(url_for('admin_personal_info'))
    
    return render_template('admin/personal_info.html', data=data)

# ==================== ADMIN CRUD - ACADEMIC ====================

@app.route('/admin/academic')
@admin_required
def admin_academic():
    """List all academic entries"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('admin/academic.html', data=data)

@app.route('/admin/academic/add', methods=['GET', 'POST'])
@admin_required
def admin_academic_add():
    """Add new academic entry"""
    if request.method == 'POST':
        data = load_portfolio_data(PORTFOLIO_DATA_PATH)
        academic = data.get('academic', [])
        
        new_entry = {
            'id': generate_id(),
            'degree': request.form.get('degree', ''),
            'institution': request.form.get('institution', ''),
            'year': request.form.get('year', ''),
            'description': request.form.get('description', '')
        }
        
        academic.append(new_entry)
        data['academic'] = academic
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Academic entry added successfully!', 'success')
            return redirect(url_for('admin_academic'))
        else:
            flash('Error adding academic entry.', 'error')
    
    return render_template('admin/academic_form.html')

@app.route('/admin/academic/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_academic_edit(item_id):
    """Edit academic entry"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    academic = data.get('academic', [])
    entry = get_item_by_id(academic, item_id)
    
    if not entry:
        flash('Academic entry not found.', 'error')
        return redirect(url_for('admin_academic'))
    
    if request.method == 'POST':
        entry['degree'] = request.form.get('degree', '')
        entry['institution'] = request.form.get('institution', '')
        entry['year'] = request.form.get('year', '')
        entry['description'] = request.form.get('description', '')
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Academic entry updated successfully!', 'success')
            return redirect(url_for('admin_academic'))
        else:
            flash('Error updating academic entry.', 'error')
    
    return render_template('admin/academic_form.html', entry=entry)

@app.route('/admin/academic/delete/<item_id>', methods=['POST'])
@admin_required
def admin_academic_delete(item_id):
    """Delete academic entry"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    academic = data.get('academic', [])
    academic = [item for item in academic if item.get('id') != item_id]
    data['academic'] = academic
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Academic entry deleted successfully!', 'success')
    else:
        flash('Error deleting academic entry.', 'error')
    
    return redirect(url_for('admin_academic'))

# ==================== ADMIN CRUD - PROJECTS ====================

@app.route('/admin/projects')
@admin_required
def admin_projects():
    """List all projects"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('admin/projects.html', data=data)

@app.route('/admin/projects/add', methods=['GET', 'POST'])
@admin_required
def admin_projects_add():
    """Add new project"""
    if request.method == 'POST':
        data = load_portfolio_data(PORTFOLIO_DATA_PATH)
        projects = data.get('projects', [])
        
        new_entry = {
            'id': generate_id(),
            'title': request.form.get('title', ''),
            'description': request.form.get('description', ''),
            'technologies': [t.strip() for t in request.form.get('technologies', '').split(',') if t.strip()],
            'github_url': request.form.get('github_url', ''),
            'live_url': request.form.get('live_url', ''),
            'image_url': request.form.get('image_url', ''),
            'start_date': request.form.get('start_date', ''),
            'end_date': request.form.get('end_date', ''),
            'featured': request.form.get('featured') == 'on',
            'screenshots': []
        }
        
        projects.append(new_entry)
        data['projects'] = projects
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Project added successfully!', 'success')
            return redirect(url_for('admin_projects'))
        else:
            flash('Error adding project.', 'error')
    
    return render_template('admin/projects_form.html')

@app.route('/admin/projects/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_projects_edit(item_id):
    """Edit project"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    projects = data.get('projects', [])
    entry = get_item_by_id(projects, item_id)
    
    if not entry:
        flash('Project not found.', 'error')
        return redirect(url_for('admin_projects'))
    
    if request.method == 'POST':
        entry['title'] = request.form.get('title', '')
        entry['description'] = request.form.get('description', '')
        entry['technologies'] = [t.strip() for t in request.form.get('technologies', '').split(',') if t.strip()]
        entry['github_url'] = request.form.get('github_url', '')
        entry['live_url'] = request.form.get('live_url', '')
        entry['image_url'] = request.form.get('image_url', '')
        entry['start_date'] = request.form.get('start_date', '')
        entry['end_date'] = request.form.get('end_date', '')
        entry['featured'] = request.form.get('featured') == 'on'
        if 'screenshots' not in entry:
            entry['screenshots'] = []
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Project updated successfully!', 'success')
            return redirect(url_for('admin_projects'))
        else:
            flash('Error updating project.', 'error')
    
    return render_template('admin/projects_form.html', entry=entry)

@app.route('/admin/projects/delete/<item_id>', methods=['POST'])
@admin_required
def admin_projects_delete(item_id):
    """Delete project"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    projects = data.get('projects', [])
    project = get_item_by_id(projects, item_id)
    
    # Delete associated screenshots
    if project and project.get('screenshots'):
        for screenshot in project['screenshots']:
            if screenshot.get('filename'):
                delete_screenshot(screenshot['filename'], PROJECT_SCREENSHOTS_FOLDER)
    
    projects = [item for item in projects if item.get('id') != item_id]
    data['projects'] = projects
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Project deleted successfully!', 'success')
    else:
        flash('Error deleting project.', 'error')
    
    return redirect(url_for('admin_projects'))

@app.route('/admin/projects/<item_id>/screenshots', methods=['GET', 'POST'])
@admin_required
def admin_project_screenshots(item_id):
    """Manage project screenshots"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    projects = data.get('projects', [])
    project = get_item_by_id(projects, item_id)
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('admin_projects'))
    
    if request.method == 'POST':
        if 'screenshot' in request.files:
            file = request.files['screenshot']
            if file and file.filename:
                filename = save_screenshot(file, PROJECT_SCREENSHOTS_FOLDER)
                if filename:
                    if 'screenshots' not in project:
                        project['screenshots'] = []
                    
                    screenshot_data = {
                        'id': generate_id(),
                        'filename': filename,
                        'caption': request.form.get('caption', ''),
                        'uploaded_at': request.form.get('uploaded_at', '')
                    }
                    project['screenshots'].append(screenshot_data)
                    
                    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
                        flash('Screenshot uploaded successfully!', 'success')
                    else:
                        flash('Error saving screenshot information.', 'error')
                else:
                    flash('Invalid file format. Please upload JPG, PNG, GIF, or WEBP.', 'error')
        
        return redirect(url_for('admin_project_screenshots', item_id=item_id))
    
    return render_template('admin/project_screenshots.html', data=data, project=project)

@app.route('/admin/projects/<item_id>/screenshots/delete/<screenshot_id>', methods=['POST'])
@admin_required
def admin_project_screenshot_delete(item_id, screenshot_id):
    """Delete a project screenshot"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    projects = data.get('projects', [])
    project = get_item_by_id(projects, item_id)
    
    if not project:
        flash('Project not found.', 'error')
        return redirect(url_for('admin_projects'))
    
    if 'screenshots' in project:
        screenshot = next((s for s in project['screenshots'] if s.get('id') == screenshot_id), None)
        if screenshot:
            if screenshot.get('filename'):
                delete_screenshot(screenshot['filename'], PROJECT_SCREENSHOTS_FOLDER)
            
            project['screenshots'] = [s for s in project['screenshots'] if s.get('id') != screenshot_id]
            
            if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
                flash('Screenshot deleted successfully!', 'success')
            else:
                flash('Error deleting screenshot.', 'error')
        else:
            flash('Screenshot not found.', 'error')
    
    return redirect(url_for('admin_project_screenshots', item_id=item_id))

# ==================== ADMIN CRUD - SKILLS ====================

@app.route('/admin/skills')
@admin_required
def admin_skills():
    """List all skills"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('admin/skills.html', data=data)

@app.route('/admin/skills/add', methods=['GET', 'POST'])
@admin_required
def admin_skills_add():
    """Add new skill"""
    if request.method == 'POST':
        data = load_portfolio_data(PORTFOLIO_DATA_PATH)
        skills = data.get('skills', [])
        
        new_entry = {
            'id': generate_id(),
            'name': request.form.get('name', ''),
            'level': int(request.form.get('level', 0)),
            'category': request.form.get('category', ''),
            'icon': request.form.get('icon', '')
        }
        
        skills.append(new_entry)
        data['skills'] = data.get('skills', [])
        data['skills'] = skills
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Skill added successfully!', 'success')
            return redirect(url_for('admin_skills'))
        else:
            flash('Error adding skill.', 'error')
    
    return render_template('admin/skills_form.html')

@app.route('/admin/skills/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_skills_edit(item_id):
    """Edit skill"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    skills = data.get('skills', [])
    entry = get_item_by_id(skills, item_id)
    
    if not entry:
        flash('Skill not found.', 'error')
        return redirect(url_for('admin_skills'))
    
    if request.method == 'POST':
        entry['name'] = request.form.get('name', '')
        entry['level'] = int(request.form.get('level', 0))
        entry['category'] = request.form.get('category', '')
        entry['icon'] = request.form.get('icon', '')
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Skill updated successfully!', 'success')
            return redirect(url_for('admin_skills'))
        else:
            flash('Error updating skill.', 'error')
    
    return render_template('admin/skills_form.html', entry=entry)

@app.route('/admin/skills/delete/<item_id>', methods=['POST'])
@admin_required
def admin_skills_delete(item_id):
    """Delete skill"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    skills = data.get('skills', [])
    skills = [item for item in skills if item.get('id') != item_id]
    data['skills'] = skills
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Skill deleted successfully!', 'success')
    else:
        flash('Error deleting skill.', 'error')
    
    return redirect(url_for('admin_skills'))

# ==================== ADMIN CRUD - CERTIFICATIONS ====================

@app.route('/admin/certifications')
@admin_required
def admin_certifications():
    """List all certifications"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    return render_template('admin/certifications.html', data=data)

@app.route('/admin/certifications/add', methods=['GET', 'POST'])
@admin_required
def admin_certifications_add():
    """Add new certification"""
    if request.method == 'POST':
        data = load_portfolio_data(PORTFOLIO_DATA_PATH)
        certifications = data.get('certifications', [])
        
        new_entry = {
            'id': generate_id(),
            'name': request.form.get('name', ''),
            'issuer': request.form.get('issuer', ''),
            'date': request.form.get('date', ''),
            'credential_id': request.form.get('credential_id', ''),
            'credential_url': request.form.get('credential_url', '')
        }
        
        certifications.append(new_entry)
        data['certifications'] = certifications
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Certification added successfully!', 'success')
            return redirect(url_for('admin_certifications'))
        else:
            flash('Error adding certification.', 'error')
    
    return render_template('admin/certifications_form.html')

@app.route('/admin/certifications/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_certifications_edit(item_id):
    """Edit certification"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    certifications = data.get('certifications', [])
    entry = get_item_by_id(certifications, item_id)
    
    if not entry:
        flash('Certification not found.', 'error')
        return redirect(url_for('admin_certifications'))
    
    if request.method == 'POST':
        entry['name'] = request.form.get('name', '')
        entry['issuer'] = request.form.get('issuer', '')
        entry['date'] = request.form.get('date', '')
        entry['credential_id'] = request.form.get('credential_id', '')
        entry['credential_url'] = request.form.get('credential_url', '')
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Certification updated successfully!', 'success')
            return redirect(url_for('admin_certifications'))
        else:
            flash('Error updating certification.', 'error')
    
    return render_template('admin/certifications_form.html', entry=entry)

@app.route('/admin/certifications/delete/<item_id>', methods=['POST'])
@admin_required
def admin_certifications_delete(item_id):
    """Delete certification"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    certifications = data.get('certifications', [])
    certifications = [item for item in certifications if item.get('id') != item_id]
    data['certifications'] = certifications
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Certification deleted successfully!', 'success')
    else:
        flash('Error deleting certification.', 'error')
    
    return redirect(url_for('admin_certifications'))

# ==================== ADMIN - CV MANAGEMENT ====================

@app.route('/admin/cv', methods=['GET', 'POST'])
@admin_required
def admin_cv():
    """Manage CV upload"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    
    if request.method == 'POST':
        if 'cv_file' in request.files:
            file = request.files['cv_file']
            if file and file.filename:
                # Delete old CV if exists
                old_cv = data.get('cv_file')
                if old_cv:
                    delete_cv_file(old_cv, CV_UPLOAD_FOLDER)
                
                # Save new CV
                filename = save_cv_file(file, CV_UPLOAD_FOLDER)
                if filename:
                    data['cv_file'] = filename
                    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
                        flash('CV uploaded successfully!', 'success')
                    else:
                        flash('Error saving CV information.', 'error')
                else:
                    flash('Invalid file format. Please upload PDF, DOC, or DOCX.', 'error')
        
        return redirect(url_for('admin_cv'))
    
    return render_template('admin/cv.html', data=data)

@app.route('/admin/cv/delete', methods=['POST'])
@admin_required
def admin_cv_delete():
    """Delete CV file"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    cv_file = data.get('cv_file')
    
    if cv_file:
        if delete_cv_file(cv_file, CV_UPLOAD_FOLDER):
            data['cv_file'] = None
            if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
                flash('CV deleted successfully!', 'success')
            else:
                flash('Error updating CV information.', 'error')
        else:
            flash('Error deleting CV file.', 'error')
    else:
        flash('No CV file to delete.', 'error')
    
    return redirect(url_for('admin_cv'))

# ==================== ADMIN - MESSAGES ====================

@app.route('/admin/messages')
@admin_required
def admin_messages():
    """View all messages"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    messages = data.get('messages', [])
    # Sort by date, newest first
    messages.sort(key=lambda x: x.get('date', ''), reverse=True)
    return render_template('admin/messages.html', data=data, messages=messages)

@app.route('/admin/messages/view/<message_id>')
@admin_required
def admin_message_view(message_id):
    """View a specific message"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    messages = data.get('messages', [])
    message = get_item_by_id(messages, message_id)
    
    if not message:
        flash('Message not found.', 'error')
        return redirect(url_for('admin_messages'))
    
    # Mark as read
    message['read'] = True
    save_portfolio_data(PORTFOLIO_DATA_PATH, data)
    
    return render_template('admin/message_view.html', data=data, message=message)

@app.route('/admin/messages/delete/<message_id>', methods=['POST'])
@admin_required
def admin_message_delete(message_id):
    """Delete a message"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    messages = data.get('messages', [])
    messages = [msg for msg in messages if msg.get('id') != message_id]
    data['messages'] = messages
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Message deleted successfully!', 'success')
    else:
        flash('Error deleting message.', 'error')
    
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/mark-read/<message_id>', methods=['POST'])
@admin_required
def admin_message_mark_read(message_id):
    """Mark message as read/unread"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    messages = data.get('messages', [])
    message = get_item_by_id(messages, message_id)
    
    if message:
        message['read'] = not message.get('read', False)
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            status = 'read' if message['read'] else 'unread'
            flash(f'Message marked as {status}.', 'success')
        else:
            flash('Error updating message.', 'error')
    else:
        flash('Message not found.', 'error')
    
    return redirect(url_for('admin_messages'))

# ==================== ADMIN - ANALYTICS ====================

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """View analytics dashboard"""
    summary = get_analytics_summary(ANALYTICS_DATA_PATH)
    return render_template('admin/analytics.html', summary=summary)

@app.route('/admin/analytics/reset', methods=['POST'])
@admin_required
def admin_analytics_reset():
    """Reset all analytics data"""
    if reset_analytics(ANALYTICS_DATA_PATH):
        flash('Analytics data reset successfully!', 'success')
    else:
        flash('Error resetting analytics data.', 'error')
    return redirect(url_for('admin_analytics'))

# ==================== ADMIN - TRANSLATIONS ====================

@app.route('/admin/translations')
@admin_required
def admin_translations():
    """Manage translations"""
    translations = load_translations()
    return render_template('admin/translations.html', translations=translations, languages=SUPPORTED_LANGUAGES)

@app.route('/admin/translations/<language>')
@admin_required
def admin_translations_language(language):
    """Edit translations for a specific language"""
    if language not in SUPPORTED_LANGUAGES:
        flash('Invalid language.', 'error')
        return redirect(url_for('admin_translations'))
    
    translations = load_translations()
    lang_translations = translations.get(language, {})
    
    return render_template('admin/translations_edit.html', 
                         language=language,
                         language_name=SUPPORTED_LANGUAGES[language],
                         translations=lang_translations)

@app.route('/admin/translations/<language>/update', methods=['POST'])
@admin_required
def admin_translations_update(language):
    """Update translations"""
    if language not in SUPPORTED_LANGUAGES:
        flash('Invalid language.', 'error')
        return redirect(url_for('admin_translations'))
    
    translations = load_translations()
    
    # Get all form data
    for key, value in request.form.items():
        if key.startswith('translation_'):
            translation_key = key.replace('translation_', '').replace('_', '.')
            if update_translation(language, translation_key, value):
                flash(f'Translation updated: {translation_key}', 'success')
            else:
                flash(f'Error updating: {translation_key}', 'error')
    
    return redirect(url_for('admin_translations_language', language=language))

# ==================== ADMIN - IMPORT/EXPORT ====================

@app.route('/admin/export', methods=['POST'])
@admin_required
def admin_export():
    """Export portfolio data"""
    from flask import send_file
    import tempfile
    
    export_path = Path(tempfile.gettempdir()) / 'portfolio_backup.json'
    
    if export_portfolio_data(PORTFOLIO_DATA_PATH, export_path):
        return send_file(
            str(export_path),
            as_attachment=True,
            download_name='portfolio_backup.json'
        )
    else:
        flash('Error exporting portfolio data.', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/import', methods=['POST'])
@admin_required
def admin_import():
    """Import portfolio data"""
    if 'import_file' in request.files:
        file = request.files['import_file']
        if file and file.filename:
            if allowed_file(file.filename, {'json'}):
                import tempfile
                temp_path = Path(tempfile.gettempdir()) / 'portfolio_import.json'
                file.save(str(temp_path))
                
                if import_portfolio_data(PORTFOLIO_DATA_PATH, temp_path):
                    flash('Portfolio data imported successfully!', 'success')
                else:
                    flash('Error importing portfolio data.', 'error')
                
                if temp_path.exists():
                    temp_path.unlink()
            else:
                flash('Invalid file format. Please upload a JSON file.', 'error')
    
    return redirect(url_for('admin_dashboard'))

# ==================== ADMIN CRUD - ARTICLES ====================

@app.route('/admin/articles')
@admin_required
def admin_articles():
    """List all articles"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    articles = data.get('articles', [])
    # Sort by date, newest first
    articles.sort(key=lambda x: x.get('published_date', ''), reverse=True)
    return render_template('admin/articles.html', data=data, articles=articles)

@app.route('/admin/articles/add', methods=['GET', 'POST'])
@admin_required
def admin_articles_add():
    """Add new article"""
    if request.method == 'POST':
        data = load_portfolio_data(PORTFOLIO_DATA_PATH)
        articles = data.get('articles', [])
        
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip() or generate_slug(title)
        
        # Ensure unique slug
        existing_slugs = [a.get('slug') for a in articles if a.get('slug')]
        counter = 1
        original_slug = slug
        while slug in existing_slugs:
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        new_entry = {
            'id': generate_id(),
            'title': title,
            'slug': slug,
            'excerpt': request.form.get('excerpt', '').strip(),
            'content': request.form.get('content', '').strip(),
            'image_url': request.form.get('image_url', '').strip(),
            'categories': [c.strip() for c in request.form.get('categories', '').split(',') if c.strip()],
            'tags': [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()],
            'published_date': request.form.get('published_date', ''),
            'read_time': request.form.get('read_time', ''),
            'published': request.form.get('published') == 'on'
        }
        
        articles.append(new_entry)
        data['articles'] = articles
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Article added successfully!', 'success')
            return redirect(url_for('admin_articles'))
        else:
            flash('Error adding article.', 'error')
    
    return render_template('admin/articles_form.html')

@app.route('/admin/articles/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_articles_edit(item_id):
    """Edit article"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    articles = data.get('articles', [])
    entry = get_item_by_id(articles, item_id)
    
    if not entry:
        flash('Article not found.', 'error')
        return redirect(url_for('admin_articles'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        slug = request.form.get('slug', '').strip() or generate_slug(title)
        
        # Ensure unique slug (excluding current article)
        existing_slugs = [a.get('slug') for a in articles if a.get('slug') and a.get('id') != item_id]
        if slug in existing_slugs:
            counter = 1
            original_slug = slug
            while slug in existing_slugs:
                slug = f"{original_slug}-{counter}"
                counter += 1
        
        entry['title'] = title
        entry['slug'] = slug
        entry['excerpt'] = request.form.get('excerpt', '').strip()
        entry['content'] = request.form.get('content', '').strip()
        entry['image_url'] = request.form.get('image_url', '').strip()
        entry['categories'] = [c.strip() for c in request.form.get('categories', '').split(',') if c.strip()]
        entry['tags'] = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
        entry['published_date'] = request.form.get('published_date', '')
        entry['read_time'] = request.form.get('read_time', '')
        entry['published'] = request.form.get('published') == 'on'
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Article updated successfully!', 'success')
            return redirect(url_for('admin_articles'))
        else:
            flash('Error updating article.', 'error')
    
    return render_template('admin/articles_form.html', entry=entry)

@app.route('/admin/articles/delete/<item_id>', methods=['POST'])
@admin_required
def admin_articles_delete(item_id):
    """Delete article"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    articles = data.get('articles', [])
    articles = [item for item in articles if item.get('id') != item_id]
    data['articles'] = articles
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Article deleted successfully!', 'success')
    else:
        flash('Error deleting article.', 'error')
    
    return redirect(url_for('admin_articles'))

# ==================== ADMIN CRUD - TESTIMONIALS ====================

@app.route('/admin/testimonials')
@admin_required
def admin_testimonials():
    """List all testimonials"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    testimonials = data.get('testimonials', [])
    # Sort by date, newest first
    testimonials.sort(key=lambda x: x.get('date', ''), reverse=True)
    return render_template('admin/testimonials.html', data=data, testimonials=testimonials)

@app.route('/admin/testimonials/add', methods=['GET', 'POST'])
@admin_required
def admin_testimonials_add():
    """Add new testimonial"""
    if request.method == 'POST':
        data = load_portfolio_data(PORTFOLIO_DATA_PATH)
        testimonials = data.get('testimonials', [])
        
        from datetime import datetime
        new_entry = {
            'id': generate_id(),
            'name': request.form.get('name', '').strip(),
            'role': request.form.get('role', '').strip(),
            'company': request.form.get('company', '').strip(),
            'content': request.form.get('content', '').strip(),
            'rating': int(request.form.get('rating', 5) or 5),
            'image_url': request.form.get('image_url', '').strip(),
            'date': request.form.get('date', datetime.now().strftime('%Y-%m-%d')),
            'featured': request.form.get('featured') == 'on'
        }
        
        testimonials.append(new_entry)
        data['testimonials'] = testimonials
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Testimonial added successfully!', 'success')
            return redirect(url_for('admin_testimonials'))
        else:
            flash('Error adding testimonial.', 'error')
    
    return render_template('admin/testimonials_form.html')

@app.route('/admin/testimonials/edit/<item_id>', methods=['GET', 'POST'])
@admin_required
def admin_testimonials_edit(item_id):
    """Edit testimonial"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    testimonials = data.get('testimonials', [])
    entry = get_item_by_id(testimonials, item_id)
    
    if not entry:
        flash('Testimonial not found.', 'error')
        return redirect(url_for('admin_testimonials'))
    
    if request.method == 'POST':
        entry['name'] = request.form.get('name', '').strip()
        entry['role'] = request.form.get('role', '').strip()
        entry['company'] = request.form.get('company', '').strip()
        entry['content'] = request.form.get('content', '').strip()
        entry['rating'] = int(request.form.get('rating', 5) or 5)
        entry['image_url'] = request.form.get('image_url', '').strip()
        entry['date'] = request.form.get('date', '')
        entry['featured'] = request.form.get('featured') == 'on'
        
        if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
            flash('Testimonial updated successfully!', 'success')
            return redirect(url_for('admin_testimonials'))
        else:
            flash('Error updating testimonial.', 'error')
    
    return render_template('admin/testimonials_form.html', entry=entry)

@app.route('/admin/testimonials/delete/<item_id>', methods=['POST'])
@admin_required
def admin_testimonials_delete(item_id):
    """Delete testimonial"""
    data = load_portfolio_data(PORTFOLIO_DATA_PATH)
    testimonials = data.get('testimonials', [])
    testimonials = [item for item in testimonials if item.get('id') != item_id]
    data['testimonials'] = testimonials
    
    if save_portfolio_data(PORTFOLIO_DATA_PATH, data):
        flash('Testimonial deleted successfully!', 'success')
    else:
        flash('Error deleting testimonial.', 'error')
    
    return redirect(url_for('admin_testimonials'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """404 error page"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error page"""
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

