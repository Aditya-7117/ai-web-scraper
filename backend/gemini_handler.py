import google.generativeai as genai


class GeminiHandler:
    """Handle Gemini AI interactions"""
    
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        # FIX: Changed from 'gemini-1.5-flash' to the latest stable model alias.
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat = None
        self.context = ""
    
    def set_context(self, content, title="", description=""):
        """Set the scraped content as context"""
        self.context = f"""
Title: {title}
Description: {description}

Content:
{content}
"""
        # Start a new chat session with context
        self.chat = self.model.start_chat(history=[
            {
                "role": "user",
                "parts": [f"I've scraped the following content from a website. Please help me answer questions about it:\n\n{self.context}"]
            },
            {
                "role": "model",
                "parts": ["I've received the scraped content. I'm ready to answer your questions about it. What would you like to know?"]
            }
        ])
    
    def ask_question(self, question):
        """Ask a question about the scraped content"""
        try:
            if not self.chat:
                return {
                    'success': False,
                    'error': 'No content loaded. Please scrape a website first.'
                }
            
            response = self.chat.send_message(question)
            
            return {
                'success': True,
                'response': response.text
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def summarize(self):
        """Generate a summary of the scraped content"""
        try:
            if not self.context:
                return {
                    'success': False,
                    'error': 'No content to summarize'
                }
            
            prompt = f"""Please provide a comprehensive summary of the following content. 
Include:
1. Main topic or purpose
2. Key points (3-5 bullet points)
3. Important details or conclusions

Content:
{self.context}"""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'response': response.text
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_insights(self, task):
        """Perform specific tasks on the content"""
        try:
            if not self.context:
                return {
                    'success': False,
                    'error': 'No content available'
                }
            
            prompt = f"""Based on the following scraped content, please {task}

Content:
{self.context}"""
            
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'response': response.text
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def clear_context(self):
        """Clear the current context and chat history"""
        self.context = ""
        self.chat = None
