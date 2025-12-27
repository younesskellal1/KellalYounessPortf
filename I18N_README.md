# Multi-Language Support (i18n) - Implementation Guide

## Overview
Your portfolio now supports **3 languages**: English, French, and Arabic with full RTL (Right-to-Left) support for Arabic.

## Features Implemented

✅ **Language Switcher**: Globe icon in navbar with dropdown  
✅ **3 Languages**: English (en), French (fr), Arabic (ar)  
✅ **RTL Support**: Automatic right-to-left layout for Arabic  
✅ **Browser Detection**: Auto-detects user's preferred language  
✅ **Session Persistence**: Language choice saved in session  
✅ **Admin Management**: Full CRUD interface for translations  
✅ **Dynamic Templates**: All UI text uses translation keys  

## Files Created/Modified

### New Files
- `i18n.py` - Translation utilities and functions
- `translations.json` - Translation storage (auto-generated)
- `templates/admin/translations.html` - Admin translation management
- `templates/admin/translations_edit.html` - Edit translations for a language

### Modified Files
- `app.py` - Added i18n context processor and language routes
- `templates/base.html` - Added language switcher and translation keys
- `templates/index.html` - Updated to use translations
- `templates/projects.html` - Updated to use translations
- `templates/skills.html` - Updated to use translations
- `templates/education.html` - Updated to use translations
- `templates/certifications.html` - Updated to use translations
- `templates/about.html` - Updated to use translations
- `templates/contact.html` - Updated to use translations
- `static/css/style.css` - Added language switcher styles and RTL support
- `static/css/admin.css` - Added admin translation styles
- `static/js/main.js` - Added language switcher JavaScript

## How It Works

### 1. Language Detection
- On first visit, detects browser language
- Falls back to English if browser language not supported
- Stores choice in Flask session

### 2. Translation System
- Translations stored in `translations.json`
- Organized by sections: `nav`, `hero`, `sections`, `pages`, `common`
- Uses dot notation: `t('nav.home')` → "Home" / "Accueil" / "الرئيسية"

### 3. Language Switcher
- Globe icon in navbar
- Dropdown shows all 3 languages
- Current language highlighted with checkmark
- Clicking a language switches immediately

### 4. RTL Support
- Arabic automatically uses RTL layout
- CSS rules adjust for right-to-left reading
- Navigation and dropdowns flip direction

## Usage

### For Users
1. Click the globe icon in the navbar
2. Select desired language (English, Français, العربية)
3. Page reloads with selected language
4. Language preference persists across pages

### For Developers

#### Using Translations in Templates
```jinja2
{{ t('nav.home') }}           <!-- Navigation -->
{{ t('hero.download_cv') }}   <!-- Hero section -->
{{ t('pages.about_title') }}  <!-- Page titles -->
{{ t('common.email') }}        <!-- Common elements -->
```

#### Adding New Translation Keys
1. Edit `i18n.py` → `get_default_translations()`
2. Add key to all 3 languages (en, fr, ar)
3. Use in template: `{{ t('your.section.key') }}`

#### Admin Translation Management
1. Login to admin dashboard
2. Go to "Translations" in sidebar
3. Click "Edit Translations" for a language
4. Update translation values
5. Save changes

## Translation Structure

```json
{
  "en": {
    "nav": { "home": "Home", ... },
    "hero": { "download_cv": "Download CV", ... },
    "sections": { "skills": "Skills", ... },
    "pages": { "my_projects": "My Projects", ... },
    "common": { "name": "Name", ... }
  },
  "fr": { ... },
  "ar": { ... }
}
```

## Admin Routes

- `/admin/translations` - View all languages
- `/admin/translations/<language>` - Edit specific language
- `/admin/translations/<language>/update` - Save translations

## Public Routes

- `/set-language/<language>` - Switch language (en/fr/ar)

## RTL (Right-to-Left) Support

Arabic automatically enables RTL:
- Navigation menu flips
- Text alignment adjusts
- Dropdowns position correctly
- All layouts adapt

CSS automatically applies:
```css
html[dir="rtl"] {
    direction: rtl;
}
```

## Adding More Languages

1. Add to `SUPPORTED_LANGUAGES` in `i18n.py`:
```python
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fr': 'Français',
    'ar': 'العربية',
    'es': 'Español'  # New language
}
```

2. Add translations to `get_default_translations()` in `i18n.py`
3. Add language option to switcher dropdown (automatic)

## Translation Keys Reference

### Navigation (`nav`)
- `home`, `projects`, `skills`, `education`, `certifications`, `about`, `contact`

### Hero Section (`hero`)
- `download_cv`, `get_in_touch`

### Sections (`sections`)
- `skills`, `featured_projects`, `education`, `view_all`, `view_all_skills`, `view_all_projects`

### Pages (`pages`)
- `my_projects`, `projects_subtitle`, `skills_title`, `skills_subtitle`, `education_title`, `education_subtitle`, `certifications_title`, `certifications_subtitle`, `about_title`, `about_subtitle`, `contact_title`, `contact_subtitle`

### Common (`common`)
- `name`, `email`, `subject`, `message`, `send`, `send_message`, `contact_info`, `phone`, `location`, `total_skills`, `categories`, `average_proficiency`, `all_skills`, `no_data`, `loading`

## Testing

1. **Test Language Switching**:
   - Click globe icon
   - Select different languages
   - Verify all text changes

2. **Test RTL**:
   - Switch to Arabic
   - Verify layout flips to RTL
   - Check navigation alignment

3. **Test Admin**:
   - Login to admin
   - Edit translations
   - Verify changes appear on site

## Troubleshooting

### Translations not showing?
- Check `translations.json` exists
- Verify translation keys match exactly
- Clear browser cache

### Language not persisting?
- Check Flask session is working
- Verify cookies enabled
- Check browser console for errors

### RTL not working?
- Verify `dir="rtl"` on `<html>` tag
- Check CSS RTL rules are loaded
- Test in different browser

## Future Enhancements

Potential improvements:
- [ ] Auto-translate portfolio content (bio, project descriptions)
- [ ] Language-specific date formats
- [ ] More languages (Spanish, German, etc.)
- [ ] Translation import/export
- [ ] Translation versioning
- [ ] Missing translation warnings

---

**Status**: ✅ Fully Implemented and Ready to Use

The multi-language system is production-ready and fully integrated with your portfolio!

