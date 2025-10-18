"""
LLM Manager for Financial Intelligence System
Handles Ollama (local) and Gemini (cloud) LLM integration
"""
import requests
import json
import logging
from typing import Dict, Any, Optional
from config.settings import Config

logger = logging.getLogger(__name__)

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    logger.warning("google-generativeai not installed - Gemini support disabled")

class LLMManager:
    """
    Manages LLM operations with Ollama and Gemini support
    Provides automatic fallback between local and cloud LLMs
    """

    def __init__(self):
        self.use_gemini = Config.USE_GEMINI
        self.ollama_url = Config.OLLAMA_BASE_URL
        self.ollama_model = Config.OLLAMA_MODEL

        # Initialize Gemini if configured
        if self.use_gemini and GENAI_AVAILABLE and Config.GEMINI_API_KEY:
            try:
                genai.configure(api_key=Config.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini LLM initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.use_gemini = False

    def generate(self, prompt: str, system_prompt: str = None, 
                temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """
        Generate text using configured LLM

        Args:
            prompt: User prompt
            system_prompt: System context
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length

        Returns:
            str: Generated text
        """
        try:
            if self.use_gemini:
                return self._generate_gemini(prompt, system_prompt, temperature)
            else:
                return self._generate_ollama(prompt, system_prompt, temperature, max_tokens)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_response(prompt)

    def _generate_ollama(self, prompt: str, system_prompt: str = None,
                        temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Generate using Ollama"""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            payload = {
                "model": self.ollama_model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._fallback_response(prompt)

        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama - is it running?")
            return self._fallback_response(prompt)
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return self._fallback_response(prompt)

    def _generate_gemini(self, prompt: str, system_prompt: str = None,
                        temperature: float = 0.7) -> str:
        """Generate using Gemini"""
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            config = {
                "temperature": temperature,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }

            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=config
            )

            return response.text

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return self._fallback_response(prompt)

    def generate_structured(self, prompt: str, schema: Dict[str, Any],
                          system_prompt: str = None) -> Dict[str, Any]:
        """
        Generate structured JSON output

        Args:
            prompt: User prompt
            schema: Expected JSON schema
            system_prompt: System context

        Returns:
            Dict: Parsed JSON response
        """
        schema_prompt = f"""
        {system_prompt or "You are a helpful financial AI assistant."}

        Respond with valid JSON matching this schema:
        {json.dumps(schema, indent=2)}

        Query: {prompt}

        Respond ONLY with valid JSON, no markdown formatting.
        """

        response = self.generate(schema_prompt, temperature=0.1)

        try:
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            return json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {response[:200]}")
            return {"error": "Invalid JSON", "raw": response}

    def _fallback_response(self, prompt: str) -> str:
        """Provide fallback response when LLM unavailable"""
        return f"Analysis unavailable - LLM service not accessible. Query: {prompt[:100]}"

    def is_available(self) -> bool:
        """Check if LLM service is available"""
        if self.use_gemini:
            return hasattr(self, 'gemini_model')
        else:
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
                return response.status_code == 200
            except:
                return False
