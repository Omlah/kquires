import openai
import os
import logging
from typing import Dict, List, Tuple
from django.conf import settings
from django.db.models import Q
from kquires.articles.models import Article
from kquires.chatbot.models import ChatbotKnowledge

logger = logging.getLogger(__name__)


class ChatbotAIService:
    """AI service for chatbot functionality"""

    def __init__(self):
        self.api_key = getattr(settings, 'OPENAI_API_KEY', None)
        self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = getattr(settings, 'OPENAI_MAX_TOKENS', 4000)
        self.temperature = getattr(settings, 'OPENAI_TEMPERATURE', 0.3)

        print(f"🤖 ChatbotAIService Initialization:")
        print(f"   API Key: {'✅ Set' if self.api_key else '❌ Not set'}")
        print(f"   Model: {self.model}")
        
        # Initialize client only if API key is available
        if self.api_key:
            try:
                print(f"🚀 Initializing OpenAI client for chatbot...")
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
                    # Try to create client and catch the exact error
                    try:
                        self.client = openai.OpenAI(api_key=self.api_key)
                        print(f"✅ Chatbot OpenAI client initialized successfully")
                    except TypeError as te:
                        print(f"🔍 Chatbot TypeError details: {te}")
                        # Try with custom HTTP client to avoid proxy issues
                        import httpx
                        http_client = httpx.Client()
                        self.client = openai.OpenAI(
                            api_key=self.api_key,
                            http_client=http_client
                        )
                        print(f"✅ Chatbot OpenAI client initialized with custom HTTP client")
                finally:
                    # Restore proxy environment variables
                    for var, value in old_proxy_vars.items():
                        os.environ[var] = value
                        
            except Exception as e:
                print(f"❌ Failed to initialize chatbot OpenAI client: {str(e)}")
                logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            print(f"❌ OpenAI API key not configured for chatbot")
            logger.warning("OpenAI API key not configured")
            self.client = None

    def search_articles(self, query: str, limit: int = 5) -> List[Article]:
        """Search for relevant articles based on query"""
        try:
            # Search in title, brief_description, and short_description
            articles = Article.objects.filter(
                Q(title__icontains=query) |
                Q(brief_description__icontains=query) |
                Q(short_description__icontains=query) |
                Q(category__name__icontains=query)
            ).filter(status='approved', visibility=True)[:limit]
            
            return list(articles)
        except Exception as e:
            logger.error(f"Error searching articles: {str(e)}")
            return []

    def search_knowledge_base(self, query: str) -> List[ChatbotKnowledge]:
        """Search the chatbot knowledge base"""
        try:
            # Simple keyword matching for now
            knowledge_entries = ChatbotKnowledge.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(keywords__icontains=query)
            ).filter(is_active=True)
            
            return list(knowledge_entries)
        except Exception as e:
            logger.error(f"Error searching knowledge base: {str(e)}")
            return []

    def generate_response(self, user_message: str, context_articles: List[Article] = None, 
                         context_knowledge: List[ChatbotKnowledge] = None) -> Dict:
        """Generate AI response based on user message and context"""
        
        print(f"🤖 Chatbot Generate Response:")
        print(f"   User Message: {user_message[:100]}...")
        print(f"   Context Articles: {len(context_articles) if context_articles else 0}")
        print(f"   Context Knowledge: {len(context_knowledge) if context_knowledge else 0}")
        print(f"   Client Available: {'✅ Yes' if self.client else '❌ No'}")
        
        if not self.client:
            print(f"❌ No OpenAI client available for chatbot")
            return self._generate_improved_fallback_response(user_message, context_articles)

        try:
            # Prepare context from articles
            article_context = ""
            referenced_articles = []
            
            if context_articles:
                article_context = "\n\nRelevant Articles:\n"
                for article in context_articles:
                    article_context += f"- {article.title}: {article.short_description or article.brief_description[:200]}...\n"
                    referenced_articles.append(article.id)

            # Prepare context from knowledge base
            knowledge_context = ""
            if context_knowledge:
                knowledge_context = "\n\nKnowledge Base:\n"
                for kb in context_knowledge:
                    knowledge_context += f"- {kb.title}: {kb.content}\n"

            # Create the prompt
            system_prompt = """You are a helpful AI assistant for a knowledge base system. Your role is to:
1. Answer questions about company policies, procedures, and information
2. Help users find relevant articles and documentation
3. Provide accurate, helpful responses based on the available information
4. If you don't know something, say so and suggest where they might find the information

Always be professional, helpful, and concise. If you reference specific articles, mention their titles."""

            user_prompt = f"""User Question: {user_message}

{article_context}
{knowledge_context}

Please provide a helpful response based on the available information. If you reference specific articles, mention their titles clearly."""

            # Make API call
            print(f"🚀 Making chatbot OpenAI API call...")
            print(f"   Model: {self.model}")
            print(f"   Max Tokens: {self.max_tokens}")
            print(f"   Temperature: {self.temperature}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            print(f"✅ Chatbot OpenAI API Response received:")
            print(f"   Usage: {response.usage}")
            print(f"   Choices: {len(response.choices)}")

            ai_response = response.choices[0].message.content
            print(f"🤖 Chatbot response length: {len(ai_response)}")
            print(f"🤖 Chatbot response preview: {ai_response[:100]}...")

            return {
                "response": ai_response,
                "referenced_articles": referenced_articles,
                "ai_analysis": {
                    "model_used": self.model,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                    "context_articles_count": len(context_articles) if context_articles else 0,
                    "context_knowledge_count": len(context_knowledge) if context_knowledge else 0
                }
            }

        except Exception as e:
            print(f"❌ Chatbot AI Error:")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            print(f"   Error Details: {repr(e)}")
            logger.error(f"Error generating AI response: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again.",
                "referenced_articles": [],
                "ai_analysis": {"error": str(e)}
            }

    def process_user_message(self, user_message: str) -> Dict:
        """Main method to process user message and generate response"""
        try:
            # Search for relevant articles
            relevant_articles = self.search_articles(user_message)
            
            # Search knowledge base
            relevant_knowledge = self.search_knowledge_base(user_message)
            
            # Generate AI response
            ai_response = self.generate_response(
                user_message, 
                relevant_articles, 
                relevant_knowledge
            )
            
            return {
                "success": True,
                "response": ai_response["response"],
                "referenced_articles": relevant_articles,
                "ai_analysis": ai_response["ai_analysis"]
            }
            
        except Exception as e:
            logger.error(f"Error processing user message: {str(e)}")
            return {
                "success": False,
                "response": "I'm sorry, I encountered an error. Please try again.",
                "referenced_articles": [],
                "ai_analysis": {"error": str(e)}
            }

    def _generate_improved_fallback_response(self, user_message: str, context_articles: List[Article] = None) -> Dict:
        """Generate improved fallback response when AI is not available"""
        
        if context_articles and len(context_articles) > 0:
            response = f"I found {len(context_articles)} relevant article(s) that might help you:\n\n"
            for i, article in enumerate(context_articles, 1):
                response += f"{i}. **{article.title}**\n"
                if article.short_description:
                    response += f"   {article.short_description}\n"
                response += f"   [Read Article](/articles/{article.id}/)\n\n"
            
            response += "These articles contain information related to your question. Click the links to read more details."
        else:
            response = f"I couldn't find specific articles related to '{user_message}'. Here are some suggestions:\n\n"
            response += "1. **Try rephrasing your question** with different keywords\n"
            response += "2. **Browse categories** to find relevant topics\n"
            response += "3. **Use the search function** to find specific information\n"
            response += "4. **Contact your administrator** for assistance\n\n"
            response += "You can also try asking about:\n"
            response += "- Getting started guides\n"
            response += "- Common procedures\n"
            response += "- Department resources\n"
            response += "- Company policies"
        
        return {
            "response": response,
            "referenced_articles": [article.id for article in context_articles] if context_articles else [],
            "ai_analysis": {
                "fallback_used": True,
                "articles_referenced": len(context_articles) if context_articles else 0
            }
        }
