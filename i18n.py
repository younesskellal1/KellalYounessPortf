"""
Internationalization (i18n) utilities for multi-language support
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps
from flask import session, request

# Translation file path
TRANSLATIONS_PATH = Path(__file__).parent / 'translations.json'

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fr': 'Français',
    'ar': 'العربية'
}

DEFAULT_LANGUAGE = 'en'

def load_translations() -> Dict[str, Any]:
    """Load translations from JSON file"""
    if not TRANSLATIONS_PATH.exists():
        # Initialize with default translations
        default_translations = get_default_translations()
        save_translations(default_translations)
        return default_translations
    
    try:
        with open(TRANSLATIONS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading translations: {e}")
        return get_default_translations()

def save_translations(translations: Dict[str, Any]) -> bool:
    """Save translations to JSON file atomically"""
    import os
    try:
        temp_path = TRANSLATIONS_PATH.with_suffix('.json.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(translations, f, indent=2, ensure_ascii=False)
        
        if os.name == 'nt':  # Windows
            if TRANSLATIONS_PATH.exists():
                os.replace(temp_path, TRANSLATIONS_PATH)
            else:
                temp_path.rename(TRANSLATIONS_PATH)
        else:  # Unix-like
            os.replace(temp_path, TRANSLATIONS_PATH)
        
        return True
    except Exception as e:
        print(f"Error saving translations: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False

def get_default_translations() -> Dict[str, Any]:
    """Get default translations for all languages"""
    import os
    return {
        'en': {
            'nav': {
                'home': 'Home',
                'projects': 'Projects',
                'skills': 'Skills',
                'education': 'Education',
                'certifications': 'Certifications',
                'about': 'About',
                'contact': 'Contact'
            },
            'hero': {
                'download_cv': 'Download CV',
                'get_in_touch': 'Get In Touch'
            },
            'sections': {
                'skills': 'Skills',
                'featured_projects': 'Featured Projects',
                'education': 'Education',
                'view_all': 'View All',
                'view_all_skills': 'View All Skills',
                'view_all_projects': 'View All Projects'
            },
            'pages': {
                'my_projects': 'My Projects',
                'projects_subtitle': 'A collection of my work and contributions',
                'skills_title': 'Skills & Technologies',
                'skills_subtitle': 'A comprehensive overview of my technical expertise',
                'education_title': 'Education',
                'education_subtitle': 'Academic journey and achievements',
                'certifications_title': 'Certifications',
                'certifications_subtitle': 'Professional certifications and achievements',
                'about_title': 'About Me',
                'about_subtitle': 'Get to know more about my journey',
                'contact_title': 'Get In Touch',
                'contact_subtitle': "Let's work together on your next project"
            },
            'common': {
                'name': 'Name',
                'email': 'Email',
                'subject': 'Subject',
                'message': 'Message',
                'send': 'Send',
                'send_message': 'Send Message',
                'contact_info': 'Contact Information',
                'phone': 'Phone',
                'location': 'Location',
                'total_skills': 'Total Skills',
                'categories': 'Categories',
                'average_proficiency': 'Average Proficiency',
                'all_skills': 'All Skills',
                'no_data': 'No data available',
                'loading': 'Loading...'
            }
        },
        'fr': {
            'nav': {
                'home': 'Accueil',
                'projects': 'Projets',
                'skills': 'Compétences',
                'education': 'Éducation',
                'certifications': 'Certifications',
                'about': 'À propos',
                'contact': 'Contact'
            },
            'hero': {
                'download_cv': 'Télécharger CV',
                'get_in_touch': 'Contactez-moi'
            },
            'sections': {
                'skills': 'Compétences',
                'featured_projects': 'Projets en vedette',
                'education': 'Éducation',
                'view_all': 'Voir tout',
                'view_all_skills': 'Voir toutes les compétences',
                'view_all_projects': 'Voir tous les projets'
            },
            'pages': {
                'my_projects': 'Mes Projets',
                'projects_subtitle': 'Une collection de mes travaux et contributions',
                'skills_title': 'Compétences et Technologies',
                'skills_subtitle': 'Un aperçu complet de mon expertise technique',
                'education_title': 'Éducation',
                'education_subtitle': 'Parcours académique et réalisations',
                'certifications_title': 'Certifications',
                'certifications_subtitle': 'Certifications professionnelles et réalisations',
                'about_title': 'À propos de moi',
                'about_subtitle': 'En savoir plus sur mon parcours',
                'contact_title': 'Contactez-moi',
                'contact_subtitle': 'Travaillons ensemble sur votre prochain projet'
            },
            'common': {
                'name': 'Nom',
                'email': 'E-mail',
                'subject': 'Sujet',
                'message': 'Message',
                'send': 'Envoyer',
                'send_message': 'Envoyer le message',
                'contact_info': 'Informations de contact',
                'phone': 'Téléphone',
                'location': 'Localisation',
                'total_skills': 'Total des compétences',
                'categories': 'Catégories',
                'average_proficiency': 'Compétence moyenne',
                'all_skills': 'Toutes les compétences',
                'no_data': 'Aucune donnée disponible',
                'loading': 'Chargement...'
            }
        },
        'ar': {
            'nav': {
                'home': 'الرئيسية',
                'projects': 'المشاريع',
                'skills': 'المهارات',
                'education': 'التعليم',
                'certifications': 'الشهادات',
                'about': 'نبذة',
                'contact': 'اتصل'
            },
            'hero': {
                'download_cv': 'تحميل السيرة الذاتية',
                'get_in_touch': 'تواصل معي'
            },
            'sections': {
                'skills': 'المهارات',
                'featured_projects': 'المشاريع المميزة',
                'education': 'التعليم',
                'view_all': 'عرض الكل',
                'view_all_skills': 'عرض جميع المهارات',
                'view_all_projects': 'عرض جميع المشاريع'
            },
            'pages': {
                'my_projects': 'مشاريعي',
                'projects_subtitle': 'مجموعة من أعمالي ومساهماتي',
                'skills_title': 'المهارات والتقنيات',
                'skills_subtitle': 'نظرة شاملة على خبرتي التقنية',
                'education_title': 'التعليم',
                'education_subtitle': 'الرحلة الأكاديمية والإنجازات',
                'certifications_title': 'الشهادات',
                'certifications_subtitle': 'الشهادات المهنية والإنجازات',
                'about_title': 'نبذة عني',
                'about_subtitle': 'تعرف على المزيد حول رحلتي',
                'contact_title': 'تواصل معي',
                'contact_subtitle': 'دعنا نعمل معًا على مشروعك القادم'
            },
            'common': {
                'name': 'الاسم',
                'email': 'البريد الإلكتروني',
                'subject': 'الموضوع',
                'message': 'الرسالة',
                'send': 'إرسال',
                'send_message': 'إرسال الرسالة',
                'contact_info': 'معلومات الاتصال',
                'phone': 'الهاتف',
                'location': 'الموقع',
                'total_skills': 'إجمالي المهارات',
                'categories': 'الفئات',
                'average_proficiency': 'الكفاءة المتوسطة',
                'all_skills': 'جميع المهارات',
                'no_data': 'لا توجد بيانات متاحة',
                'loading': 'جاري التحميل...'
            }
        }
    }

def get_current_language() -> str:
    """Get current language from session or default"""
    return session.get('language', DEFAULT_LANGUAGE)

def set_language(language: str) -> None:
    """Set language in session"""
    if language in SUPPORTED_LANGUAGES:
        session['language'] = language

def get_translation(key: str, language: Optional[str] = None) -> str:
    """Get translation for a key in the specified or current language"""
    if language is None:
        language = get_current_language()
    
    translations = load_translations()
    lang_translations = translations.get(language, translations.get(DEFAULT_LANGUAGE, {}))
    
    # Navigate nested keys (e.g., 'nav.home')
    keys = key.split('.')
    value = lang_translations
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            return key  # Return key if translation not found
    
    return value if value else key

def get_translations_for_language(language: str) -> Dict[str, Any]:
    """Get all translations for a specific language"""
    translations = load_translations()
    return translations.get(language, translations.get(DEFAULT_LANGUAGE, {}))

def update_translation(language: str, key: str, value: str) -> bool:
    """Update a translation"""
    translations = load_translations()
    
    if language not in translations:
        translations[language] = {}
    
    # Navigate nested keys
    keys = key.split('.')
    current = translations[language]
    
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    
    current[keys[-1]] = value
    
    return save_translations(translations)

