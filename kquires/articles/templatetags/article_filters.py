from django import template

register = template.Library()

@register.filter
def get_title_for_language(article, language):
    """Get article title in specified language"""
    return article.get_title_for_language(language)

@register.filter
def get_short_description_for_language(article, language):
    """Get article short description in specified language"""
    return article.get_short_description_for_language(language)

@register.filter
def get_brief_description_for_language(article, language):
    """Get article brief description in specified language"""
    return article.get_brief_description_for_language(language)
