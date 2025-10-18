"""
Configuration Management for Financial Intelligence System
Loads and validates all configuration from environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration from environment variables"""

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # LLM Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    USE_GEMINI = os.getenv('USE_GEMINI', 'False').lower() == 'true'
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # API Keys
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    POLYGON_API_KEY = os.getenv('POLYGON_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    FRED_API_KEY = os.getenv('FRED_API_KEY', '')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///financial_data.db')

    # Risk Management
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.10))
    VAR_CONFIDENCE = float(os.getenv('VAR_CONFIDENCE', 0.95))
    RISK_FREE_RATE = float(os.getenv('RISK_FREE_RATE', 0.045))

    # System Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    CACHE_TTL = int(os.getenv('CACHE_TTL', 300))
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        warnings = []

        if not cls.ALPHA_VANTAGE_API_KEY:
            warnings.append("ALPHA_VANTAGE_API_KEY not set - market data will be limited")

        if not cls.USE_GEMINI and not cls._check_ollama():
            warnings.append("Ollama not available and Gemini not configured - LLM features disabled")

        return warnings

    @staticmethod
    def _check_ollama():
        """Check if Ollama is available"""
        try:
            import requests
            response = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
