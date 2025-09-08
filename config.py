"""
Configuration module for DELINEATE AND DECIPHER application.
Contains all configuration settings, environment variables, and constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class containing all application settings."""
    
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Configuration
    EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
    RERANKING_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'
    
    # Groq API Configuration
    GROQ_MODEL = "openai/gpt-oss-20b"
    GROQ_TEMPERATURE = 1
    GROQ_MAX_TOKENS = 8192
    GROQ_TOP_P = 1
    GROQ_REASONING_EFFORT = "medium"
    GROQ_STREAM = False
    GROQ_TOOLS = [{"type": "code_interpreter"}, {"type": "browser_search"}]
    
    # Text Processing Configuration
    TEXT_SPLITTER_CONFIG = {
        "separators": ["\n\n", "\n", ". ", "?", "!", " ", ""],
        "chunk_size": 512,
        "chunk_overlap": 128,
        "length_function": len
    }
    
    # PDF Processing Configuration
    HEADING_REGEX_PATTERN = r"^(CHAPTER \d+|(\d{1,2}(\.\d{1,2})*))\s+([A-Z][A-Za-z\s,:-]+)$"
    DEFAULT_HEADING = "Introduction"
    
    # Retrieval Configuration
    SEMANTIC_SEARCH_TOP_K = 20
    STRUCTURAL_SEARCH_TOP_K = 10
    SEMANTIC_FALLBACK_TOP_K = 5
    
    # UI Configuration
    APP_TITLE = "DELINEATE AND DECIPHER"
    APP_ICON = "🧠"
    LAYOUT = "wide"
    
    # Navigation Menu
    MENU_OPTIONS = ["🏠 Home", "✍️ Delineate", "🔍 Decipher", "ℹ️ About"]
    
    # Math Solver URL
    MATH_SOLVER_URL = "https://newfrontend-gray.vercel.app/"
    
    @classmethod
    def validate_config(cls):
        """Validate essential configuration."""
        if not cls.GROQ_API_KEY:
            return False, "GROQ_API_KEY not found in environment variables"
        return True, "Configuration validated successfully"