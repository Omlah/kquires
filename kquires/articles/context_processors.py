def current_language(request):
    """Context processor to get current language from cookie or session"""
    # Get language from cookie (set by navbar language switcher)
    language = request.COOKIES.get('language', 'en')
    
    # Map language codes to our internal format
    language_mapping = {
        'en': 'english',
        'ar': 'arabic'
    }
    
    current_lang = language_mapping.get(language, 'english')
    
    return {
        'current_language': current_lang,
        'current_language_code': language,
        'is_arabic': current_lang == 'arabic',
        'is_english': current_lang == 'english'
    }
