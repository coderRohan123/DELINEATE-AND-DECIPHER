"""
Utility functions for DELINEATE AND DECIPHER application.
Contains helper functions, validation utilities, and common operations.
"""

import os
import re
import tempfile
from typing import List, Dict, Tuple, Any, Optional
import streamlit as st
from config import Config

def validate_environment() -> Tuple[bool, List[str]]:
    """
    Validate the application environment and dependencies.
    
    Returns:
        Tuple[bool, List[str]]: Validation status and list of issues
    """
    issues = []
    
    # Check API key configuration
    if not Config.GROQ_API_KEY:
        issues.append("GROQ_API_KEY not found in environment variables")
    
    # Check required directories
    if not os.path.exists("./assets"):
        os.makedirs("./assets", exist_ok=True)
    
    return len(issues) == 0, issues

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove invalid characters for filenames
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def truncate_text(text: str, max_length: int = 250, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text (str): Original text
        max_length (int): Maximum length
        suffix (str): Suffix to add when truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.
    
    Args:
        text (str): Original text
        
    Returns:
        str: Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,!?;:()[\]{}"\']', '', text)
    return text.strip()

def extract_page_numbers(text: str) -> List[int]:
    """
    Extract page numbers mentioned in text.
    
    Args:
        text (str): Text to search
        
    Returns:
        List[int]: List of page numbers found
    """
    # Pattern to match page references like "Page 5", "p. 10", "pp. 15-20"
    patterns = [
        r'[Pp]age\s+(\d+)',
        r'[Pp]\.\s*(\d+)',
        r'[Pp]p\.\s*(\d+)(?:-\d+)?'
    ]
    
    page_numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        page_numbers.extend([int(match) for match in matches])
    
    return sorted(list(set(page_numbers)))

def create_safe_temp_file(content: str, suffix: str = ".txt") -> str:
    """
    Create a temporary file with content safely.
    
    Args:
        content (str): Content to write to file
        suffix (str): File suffix
        
    Returns:
        str: Path to temporary file
    """
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=suffix, encoding='utf-8')
    temp_file.write(content)
    temp_file.close()
    return temp_file.name

def safe_delete_temp_file(file_path: str) -> bool:
    """
    Safely delete a temporary file.
    
    Args:
        file_path (str): Path to file to delete
        
    Returns:
        bool: Success status
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            return True
        return False
    except Exception:
        return False

def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate basic text similarity using Jaccard similarity.
    
    Args:
        text1 (str): First text
        text2 (str): Second text
        
    Returns:
        float: Similarity score between 0 and 1
    """
    # Simple word-based Jaccard similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0.0
    
    return len(intersection) / len(union)

def format_citation(page_number: int, section: str) -> str:
    """
    Format a citation string consistently.
    
    Args:
        page_number (int): Page number
        section (str): Section name
        
    Returns:
        str: Formatted citation
    """
    return f"[Page {page_number}, {section}]"

def extract_section_number(heading: str) -> Optional[str]:
    """
    Extract section number from a heading.
    
    Args:
        heading (str): Heading text
        
    Returns:
        Optional[str]: Section number if found
    """
    # Match patterns like "1.2.3", "Chapter 5", etc.
    patterns = [
        r'^(\d+(?:\.\d+)*)',  # 1.2.3 format
        r'^[Cc]hapter\s+(\d+)',  # Chapter format
        r'^[Ss]ection\s+(\d+(?:\.\d+)*)'  # Section format
    ]
    
    for pattern in patterns:
        match = re.match(pattern, heading.strip())
        if match:
            return match.group(1)
    
    return None

def generate_summary_stats(chunks: List[Dict]) -> Dict[str, Any]:
    """
    Generate summary statistics for processed chunks.
    
    Args:
        chunks (List[Dict]): List of text chunks
        
    Returns:
        Dict[str, Any]: Summary statistics
    """
    if not chunks:
        return {
            "total_chunks": 0,
            "total_words": 0,
            "avg_chunk_length": 0,
            "unique_pages": 0,
            "unique_sections": 0
        }
    
    total_words = sum(len(chunk['text'].split()) for chunk in chunks)
    avg_length = total_words / len(chunks)
    unique_pages = len(set(chunk['page_number'] for chunk in chunks))
    unique_sections = len(set(chunk['heading'] for chunk in chunks))
    
    return {
        "total_chunks": len(chunks),
        "total_words": total_words,
        "avg_chunk_length": round(avg_length, 1),
        "unique_pages": unique_pages,
        "unique_sections": unique_sections
    }

def validate_pdf_file(uploaded_file) -> Tuple[bool, str]:
    """
    Validate uploaded PDF file.
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        Tuple[bool, str]: Validation status and message
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    if not uploaded_file.name.lower().endswith('.pdf'):
        return False, "File must be a PDF"
    
    # Check file size (limit to 50MB)
    if uploaded_file.size > 50 * 1024 * 1024:
        return False, "File size must be less than 50MB"
    
    if uploaded_file.size == 0:
        return False, "File appears to be empty"
    
    return True, "File validation passed"

def format_elapsed_time(start_time: float, end_time: float) -> str:
    """
    Format elapsed time in human-readable format.
    
    Args:
        start_time (float): Start timestamp
        end_time (float): End timestamp
        
    Returns:
        str: Formatted time string
    """
    elapsed = end_time - start_time
    
    if elapsed < 1:
        return f"{elapsed*1000:.0f} ms"
    elif elapsed < 60:
        return f"{elapsed:.1f} seconds"
    else:
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        return f"{minutes}m {seconds:.1f}s"

def create_error_report(error: Exception, context: str = "") -> Dict[str, str]:
    """
    Create a structured error report.
    
    Args:
        error (Exception): The exception that occurred
        context (str): Additional context about when the error occurred
        
    Returns:
        Dict[str, str]: Error report
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "suggestion": get_error_suggestion(error)
    }

def get_error_suggestion(error: Exception) -> str:
    """
    Get a user-friendly suggestion based on the error type.
    
    Args:
        error (Exception): The exception
        
    Returns:
        str: Suggested action
    """
    error_type = type(error).__name__
    
    suggestions = {
        "FileNotFoundError": "Please check if the file exists and is accessible.",
        "PermissionError": "Please check file permissions or try running with elevated privileges.",
        "MemoryError": "The file might be too large. Try with a smaller PDF.",
        "ValueError": "Please check if the input values are correct and properly formatted.",
        "ConnectionError": "Please check your internet connection and API configuration.",
        "TimeoutError": "The operation timed out. Please try again or check your connection."
    }
    
    return suggestions.get(error_type, "Please try again or contact support if the issue persists.")

class PerformanceMonitor:
    """Simple performance monitoring utility."""
    
    def __init__(self):
        self.timings = {}
    
    def start_timing(self, operation: str):
        """Start timing an operation."""
        import time
        self.timings[operation] = {"start": time.time()}
    
    def end_timing(self, operation: str):
        """End timing an operation."""
        import time
        if operation in self.timings:
            self.timings[operation]["end"] = time.time()
            self.timings[operation]["duration"] = (
                self.timings[operation]["end"] - self.timings[operation]["start"]
            )
    
    def get_timing(self, operation: str) -> Optional[float]:
        """Get timing for an operation."""
        if operation in self.timings and "duration" in self.timings[operation]:
            return self.timings[operation]["duration"]
        return None
    
    def get_all_timings(self) -> Dict[str, float]:
        """Get all timing data."""
        return {
            op: data.get("duration", 0) 
            for op, data in self.timings.items() 
            if "duration" in data
        }