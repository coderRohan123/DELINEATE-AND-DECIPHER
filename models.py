"""
AI Models module for DELINEATE AND DECIPHER application.
Handles initialization and caching of AI models including embeddings, reranking, and API clients.
"""

import streamlit as st
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from groq import Groq
from config import Config

@st.cache_resource
def get_groq_client():
    """
    Initialize and cache the Groq API client.
    
    Returns:
        Groq: Groq client instance or None if API key not configured
    """
    if not Config.GROQ_API_KEY:
        return None
    return Groq(api_key=Config.GROQ_API_KEY)

@st.cache_resource
def load_embedding_model():
    """
    Load and cache the sentence transformer model for creating embeddings.
    
    Returns:
        SentenceTransformer: Embedding model instance
    """
    return SentenceTransformer(Config.EMBEDDING_MODEL_NAME)

@st.cache_resource
def load_reranking_model():
    """
    Load and cache the cross-encoder model for re-ranking search results.
    
    Returns:
        CrossEncoder: Re-ranking model instance
    """
    return CrossEncoder(Config.RERANKING_MODEL_NAME)

@st.cache_resource
def get_text_splitter():
    """
    Initialize and cache the text splitter with optimized parameters.
    
    Returns:
        RecursiveCharacterTextSplitter: Text splitter instance
    """
    return RecursiveCharacterTextSplitter(**Config.TEXT_SPLITTER_CONFIG)

def call_groq_api(prompt: str, context: str) -> str:
    """
    Call the Groq API with the advanced prompt for question answering.
    
    Args:
        prompt (str): User's question
        context (str): Retrieved context from documents
        
    Returns:
        str: Generated response from the model
    """
    client = get_groq_client()
    if not client:
        return "⚠️ GROQ_API_KEY not configured."

    system_message = f"""You are a highly precise Q&A assistant. Your task is to answer user questions based ONLY on the provided context.
- Provide a clear, concise, and direct answer.
- For every piece of information, you MUST cite the page and section it came from in brackets, like this: [Page 19, 5.5 DISCUSSION].
- If the answer is not in the context, state: "The answer is not available in the provided document sections."
- Do not use external knowledge.

Context:
{context}
"""
    
    try:
        completion = client.chat.completions.create(
            model=Config.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=Config.GROQ_TEMPERATURE,
            max_completion_tokens=Config.GROQ_MAX_TOKENS,
            top_p=Config.GROQ_TOP_P,
            reasoning_effort=Config.GROQ_REASONING_EFFORT,
            stream=Config.GROQ_STREAM,
            stop=None,
            tools=Config.GROQ_TOOLS
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error calling Groq API: {e}"

class ModelManager:
    """
    Manager class for handling all AI models and their lifecycle.
    """
    
    def __init__(self):
        self.embedding_model = None
        self.reranking_model = None
        self.text_splitter = None
        self.groq_client = None
    
    def initialize_models(self):
        """Initialize all required models."""
        self.embedding_model = load_embedding_model()
        self.reranking_model = load_reranking_model()
        self.text_splitter = get_text_splitter()
        self.groq_client = get_groq_client()
        return self
    
    def validate_models(self):
        """Validate that all models are properly loaded."""
        models_status = {
            "embedding_model": self.embedding_model is not None,
            "reranking_model": self.reranking_model is not None,
            "text_splitter": self.text_splitter is not None,
            "groq_client": self.groq_client is not None
        }
        return all(models_status.values()), models_status