"""
Translation service utilities for the kquires project.
This module provides functions for language detection and text translation.
"""

import json
import re
from typing import Dict, Any, Optional


def detect_language(text: str) -> str:
    """
    Detect the language of the given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: The detected language ('english' or 'arabic')
    """
    if not text:
        return 'english'
    
    # Simple heuristic: check for Arabic characters
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    total_chars = len([char for char in text if char.isalpha()])
    
    if total_chars == 0:
        return 'english'
    
    arabic_ratio = arabic_chars / total_chars
    
    # If more than 30% of characters are Arabic, consider it Arabic
    if arabic_ratio > 0.3:
        return 'arabic'
    else:
        return 'english'


def translate_text(text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """
    Translate text from source language to target language.
    
    Args:
        text (str): The text to translate
        source_lang (str): Source language ('english' or 'arabic')
        target_lang (str): Target language ('english' or 'arabic')
        
    Returns:
        Dict[str, Any]: Translation result with 'translated_text' key
    """
    if not text:
        return {'translated_text': text}
    
    # If source and target are the same, return original text
    if source_lang == target_lang:
        return {'translated_text': text}
    
    try:
        # Try to use the AI service if available
        from kquires.articles.ai_services import ai_service
        return ai_service.translate_content(text, source_lang, target_lang)
    except ImportError:
        # Fallback: return original text if AI service is not available
        return {'translated_text': text}
    except Exception as e:
        # If translation fails, return original text
        print(f"Translation failed: {e}")
        return {'translated_text': text}


def clean_ai_json(text: str) -> str:
    """
    Clean AI-generated JSON text by extracting the actual content.
    
    Args:
        text (str): The text that might contain JSON formatting
        
    Returns:
        str: Cleaned text content
    """
    if not text:
        return text
    
    # Check if the text looks like a JSON string
    if isinstance(text, str) and text.strip().startswith('{') and text.strip().endswith('}'):
        try:
            data = json.loads(text)
            # If it's a translation response, extract the translated text
            if isinstance(data, dict) and 'translated_text' in data:
                return data['translated_text']
            # If it's a translation response, extract the original text
            elif isinstance(data, dict) and 'original_text' in data:
                return data['original_text']
        except (json.JSONDecodeError, TypeError):
            pass
    
    return text


def extract_clean_text(text: str) -> str:
    """
    Extract clean text from potentially JSON-formatted text.
    This is an alias for clean_ai_json for backward compatibility.
    
    Args:
        text (str): The text to clean
        
    Returns:
        str: Cleaned text content
    """
    return clean_ai_json(text)
