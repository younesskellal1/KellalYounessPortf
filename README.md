# Futuristic Portfolio Application

A professional, futuristic portfolio application built with Flask and modern frontend technologies. Features a JSON-based backend and a comprehensive Admin Dashboard.

## Features

- **Futuristic UI/UX Design**: Dark-themed aesthetic with neon accents and glassmorphism effects
- **3D Animations**: GSAP scroll-triggered animations and Three.js particle background
- **Admin Dashboard**: Full CRUD operations for all portfolio data
- **CV Management**: Upload and manage PDF CV files
- **Responsive Design**: Mobile-first approach with smooth transitions
- **Error Pages**: Custom 404 and 500 error pages matching the theme

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Animations**: GSAP, Three.js
- **Icons**: Font Awesome
- **Fonts**: Orbitron, Rajdhani (Google Fonts)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd portf
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (optional):
```bash
# Set these in your environment or modify config.py
# NOTE: Admin credentials are now managed in the application's SQLite database.
# The app will create a default admin user if none exists (username: admin, password: admin12345).
export SECRET_KEY="your-secret-key-here"
```

5. Run the application:
```bash
python app.py
```

6. Access the application:
- Public site: http://localhost:5000
- Admin dashboard: http://localhost:5000/admin/login
  - Default credentials (created in DB if none present): admin / admin12345 (change in production!)

## Project Structure

```
portf/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── utils.py               # Utility functions for JSON CRUD
├── portfolio_data.json    # JSON database
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── projects.html     # Projects page
│   ├── about.html        # About page
│   ├── contact.html      # Contact page
│   ├── admin/
│   │   ├── base.html     # Admin base template
│   │   ├── login.html    # Admin login
│   │   ├── dashboard.html
│   │   ├── personal_info.html
│   │   ├── projects.html
│   │   ├── projects_form.html
│   │   ├── academic.html
│   │   ├── academic_form.html
│   │   ├── skills.html
│   │   ├── skills_form.html
│   │   ├── certifications.html
│   │   ├── certifications_form.html
│   │   └── cv.html
│   └── errors/
│       ├── 404.html
│       └── 500.html
└── static/
    ├── css/
    │   ├── style.css     # Main stylesheet (1000+ lines)
    │   └── admin.css      # Admin dashboard styles
    ├── js/
    │   ├── main.js       # Main JavaScript
    │   └── admin.js      # Admin JavaScript
    ├── images/           # Image assets
    └── uploads/
        └── cv/           # CV uploads directory
```

## Admin Dashboard Features

The admin dashboard provides full CRUD operations for:

- **Personal Information**: Name, title, bio, contact info, social links
- **Projects**: Add, edit, delete projects with images, technologies, and links
- **Academic**: Manage education history
- **Skills**: Add skills with proficiency levels and categories
- **Certifications**: Track professional certifications
- **CV Management**: Upload and manage PDF CV files
- **Import/Export**: Backup and restore portfolio data

## Customization

### Changing Colors

Edit the CSS variables in `static/css/style.css`:

```css
:root {
    --color-primary: #00f0ff;
    --color-secondary: #ff00ff;
    --color-accent: #00ff88;
    /* ... */
}
```

### Adding New Sections

1. Add the data structure to `portfolio_data.json`
2. Create routes in `app.py`
3. Create templates in `templates/`
4. Add admin CRUD routes if needed

## Security Notes

⚠️ **Important**: Before deploying to production:

1. Change the `SECRET_KEY` in `config.py` or set it as an environment variable
2. Change the default admin credentials (`ADMIN_USERNAME` and `ADMIN_PASSWORD`)
3. Use environment variables for sensitive configuration
4. Implement proper authentication (consider Flask-Login or similar)
5. Add rate limiting for admin routes
6. Validate and sanitize all user inputs
7. Use HTTPS in production

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the repository.

---

Built with ❤️ using Flask and modern web technologies.

