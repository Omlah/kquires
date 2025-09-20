"""AI Services for content analysis, translation, and article generation"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.utils.translation import gettext as _
import openai
from langdetect import detect, LangDetectException
import PyPDF2
import docx
from io import BytesIO

logger = logging.getLogger(__name__)

class AIService:
    
    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 4000)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.3)
        
        
        # Initialize client only if API key is available
        if self.api_key:
            try:
                # Create client with minimal parameters to avoid django-environ conflicts
                import os
                # Temporarily clear any proxy-related environment variables
                old_proxy_vars = {}
                
                proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
                for var in proxy_vars:
                    if var in os.environ:
                        old_proxy_vars[var] = os.environ[var]
                        del os.environ[var]
                
                try:
                    # Debug: Check what parameters are being passed
                    
                    # Try to create client and catch the exact error
                    try:
                        self.client = openai.OpenAI(api_key=self.api_key)
                    except TypeError as te:
                        # Try with custom HTTP client to avoid proxy issues
                        import httpx
                        http_client = httpx.Client()
                        self.client = openai.OpenAI(
                            api_key=self.api_key,
                            http_client=http_client
                        )
                finally:
                    # Restore proxy environment variables
                    for var, value in old_proxy_vars.items():
                        os.environ[var] = value
                        
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            logger.warning("OpenAI API key not configured")
            self.client = None
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from various file types"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_extension in ['.docx', '.doc']:
                return self._extract_docx_text(file_path)
            elif file_extension in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from file {file_path}: {str(e)}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting PDF text: {str(e)}")
            return ""
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting DOCX text: {str(e)}")
            return ""
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the given text"""
        try:
            if not text or len(text.strip()) < 10:
                return 'unknown'
            
            # Use langdetect for initial detection
            detected_lang = detect(text)
            
            # Map common language codes to our supported languages
            lang_mapping = {
                'en': 'english',
                'ar': 'arabic',
            }
            
            return lang_mapping.get(detected_lang, detected_lang)
        except LangDetectException:
            # Fallback to OpenAI for language detection if client is available
            if self.client:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a language detection expert. Identify the language of the given text and respond with only the language name in English (e.g., 'english', 'arabic')."
                            },
                            {
                                "role": "user",
                                "content": f"Detect the language of this text: {text[:500]}"
                            }
                        ],
                        max_tokens=10,
                        temperature=0.1
                    )
                    return response.choices[0].message.content.strip().lower()
                except Exception as e:
                    logger.error(f"Error in AI language detection: {str(e)}")
                    return 'unknown'
            else:
                logger.warning("OpenAI client not available for language detection")
                return 'unknown'
    
    def analyze_content(self, file_path: str) -> Dict:
        """Analyze uploaded file content and extract key information"""
        try:
            text = self._extract_text_from_file(file_path)
            if not text:
                return {"error": "Could not extract text from file"}
            
            # Detect language
            language = self.detect_language(text)
            
            # Check if AI client is available
            if not self.client:
                return {
                    "language": language,
                    "text_content": text,
                    "ai_analysis": "AI analysis not available - OpenAI client not configured",
                    "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
                }
            
            # Analyze content with AI
            analysis_prompt = f"""
            Analyze the following content and provide:
            1. A brief summary (2-3 sentences)
            2. Key topics and themes
            3. Technical terms or jargon that should be preserved in translation
            4. Suggested article title
            5. Content type (tutorial, documentation, guide, etc.)
            
            Content: {text[:2000]}
            
            Respond in JSON format:
            {{
                "summary": "brief summary here",
                "topics": ["topic1", "topic2", "topic3"],
                "technical_terms": ["term1", "term2"],
                "suggested_title": "suggested title here",
                "content_type": "tutorial/documentation/guide/etc"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content analysis expert. Analyze the provided content and extract key information in the requested JSON format."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse AI response
            ai_analysis = response.choices[0].message.content.strip()
            
            return {
                "language": language,
                "text_content": text,
                "ai_analysis": ai_analysis,
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing content: {str(e)}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def translate_content(self, text: str, source_lang: str, target_lang: str, 
                         technical_terms: List[str] = None) -> Dict:
        """Translate content between languages with technical term preservation"""
        try:
            
            if not text or len(text.strip()) < 10:
                return {"error": "No content to translate"}
            
            # Prepare technical terms preservation instruction
            terms_instruction = ""
            if technical_terms:
                terms_list = ", ".join(technical_terms)
                terms_instruction = f"""
                IMPORTANT: Preserve these technical terms exactly as they are: {terms_list}
                Do not translate these terms, keep them in their original form.
                """
            
            # Language mapping
            lang_mapping = {
                'english': 'English',
                'arabic': 'Arabic',
            }
            
            source_lang_name = lang_mapping.get(source_lang, source_lang)
            target_lang_name = lang_mapping.get(target_lang, target_lang)
            
            translation_prompt = f"""
            Translate the following text from {source_lang_name} to {target_lang_name}.
            {terms_instruction}
            
            Guidelines:
            1. Maintain the original meaning and tone
            2. Preserve technical terms and proper nouns
            3. Keep formatting and structure intact
            4. Ensure the translation is natural and fluent
            5. For Arabic translations, use proper Arabic grammar and terminology
            
            Text to translate:
            {text}
            
            Provide only the translated text without any additional commentary.
            """
            
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": f"You are a professional translator specializing in {source_lang_name} to {target_lang_name} translation. Provide accurate, natural translations while preserving technical terms."
                    },
                    {"role": "user", "content": translation_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.2
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                "original_text": text,
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "technical_terms_preserved": technical_terms or []
            }
            
        except Exception as e:
            logger.error(f"Error translating content: {str(e)}")
            return {"error": f"Translation failed: {str(e)}"}
    
    def generate_article_draft(self, content_analysis: Dict, category_suggestions: List[str] = None) -> Dict:
        """Generate an article draft from analyzed content"""
        try:
            if "error" in content_analysis:
                return {"error": "Cannot generate draft from invalid analysis"}
            
            text_content = content_analysis.get("text_content", "")
            language = content_analysis.get("language", "english")
            
            # Parse AI analysis if it's a string
            ai_analysis = content_analysis.get("ai_analysis", "")
            if isinstance(ai_analysis, str):
                # Try to extract information from the AI analysis string
                summary = "Content analysis available"
                topics = []
                technical_terms = []
                suggested_title = "Generated Article"
            else:
                summary = ai_analysis.get("summary", "")
                topics = ai_analysis.get("topics", [])
                technical_terms = ai_analysis.get("technical_terms", [])
                suggested_title = ai_analysis.get("suggested_title", "Generated Article")
            
            generation_prompt = f"""
            Create a well-structured article draft based on the following content analysis:
            
            Original Content: {text_content[:1500]}
            Language: {language}
            Summary: {summary}
            Topics: {', '.join(topics) if topics else 'General'}
            Technical Terms: {', '.join(technical_terms) if technical_terms else 'None specified'}
            Suggested Title: {suggested_title}
            
            Create an article with:
            1. A compelling title
            2. A brief introduction
            3. Well-organized sections with clear headings
            4. Practical information and examples
            5. A conclusion
            
            Make the article informative, well-structured, and suitable for a knowledge base.
            Use markdown formatting for headings and structure.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a technical writer creating knowledge base articles. Create well-structured, informative articles that are easy to understand and follow."
                    },
                    {"role": "user", "content": generation_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.4
            )
            
            article_draft = response.choices[0].message.content.strip()
            
            return {
                "title": suggested_title,
                "content": article_draft,
                "language": language,
                "topics": topics,
                "technical_terms": technical_terms,
                "status": "draft",
                "requires_approval": True
            }
            
        except Exception as e:
            logger.error(f"Error generating article draft: {str(e)}")
            return {"error": f"Article generation failed: {str(e)}"}
    
    def suggest_categories(self, content_analysis: Dict, existing_categories: List[str] = None) -> Dict:
        """Suggest appropriate categories for the content"""
        try:
            if "error" in content_analysis:
                return {"error": "Cannot suggest categories from invalid analysis"}
            
            text_content = content_analysis.get("text_content", "")
            language = content_analysis.get("language", "english")
            
            # Get existing categories for context
            existing_cats = existing_categories or []
            existing_context = f"Existing categories: {', '.join(existing_cats)}" if existing_cats else "No existing categories provided"
            
            suggestion_prompt = f"""
            Based on the following content, suggest appropriate main and sub categories for a knowledge base article.
            
            Content: {text_content[:1000]}
            Language: {language}
            {existing_context}
            
            Provide suggestions in JSON format:
            {{
                "main_category": "suggested main category name",
                "sub_category": "suggested sub category name",
                "reasoning": "brief explanation of why these categories fit",
                "alternative_categories": [
                    {{"main": "alternative main", "sub": "alternative sub"}}
                ]
            }}
            
            Consider:
            1. The main topic and subject area
            2. The technical level and audience
            3. The content type (tutorial, reference, guide, etc.)
            4. Logical hierarchy and organization
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a knowledge management expert. Suggest logical, well-organized categories for content based on its subject matter and purpose."
                    },
                    {"role": "user", "content": suggestion_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            suggestions = response.choices[0].message.content.strip()
            
            return {
                "suggestions": suggestions,
                "content_language": language,
                "analysis_timestamp": content_analysis.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Error suggesting categories: {str(e)}")
            return {"error": f"Category suggestion failed: {str(e)}"}
    
    def enhance_search_suggestions(self, query: str, existing_articles: List[Dict] = None) -> Dict:
        """Enhance search with AI-powered suggestions"""
        try:
            if not query or len(query.strip()) < 2:
                return {"error": "Query too short"}
            
            # Prepare context from existing articles
            articles_context = ""
            if existing_articles:
                articles_context = "Existing articles in the knowledge base:\n"
                for article in existing_articles[:10]:  # Limit to first 10 for context
                    articles_context += f"- {article.get('title', 'Untitled')}: {article.get('summary', 'No summary')}\n"
            
            enhancement_prompt = f"""
            User search query: "{query}"
            
            {articles_context}
            
            Provide enhanced search suggestions in JSON format:
            {{
                "enhanced_query": "improved search query with better keywords",
                "related_queries": ["related query 1", "related query 2", "related query 3"],
                "suggested_articles": [
                    {{"title": "suggested article title", "reason": "why this might be relevant"}}
                ],
                "search_tips": ["tip 1", "tip 2"]
            }}
            
            Consider:
            1. Synonyms and alternative terms
            2. Common misspellings or variations
            3. Related technical concepts
            4. User intent and context
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a search enhancement expert. Help users find relevant content by improving their search queries and suggesting related content."
                    },
                    {"role": "user", "content": enhancement_prompt}
                ],
                max_tokens=600,
                temperature=0.3
            )
            
            enhancements = response.choices[0].message.content.strip()
            
            return {
                "original_query": query,
                "enhancements": enhancements,
                "timestamp": "now"
            }
            
        except Exception as e:
            logger.error(f"Error enhancing search: {str(e)}")
            return {"error": f"Search enhancement failed: {str(e)}"}


# Global instance
ai_service = AIService()
