"""
PDF Processing module for DELINEATE AND DECIPHER application.
Handles PDF text extraction, structure analysis, and chunk creation.
"""

import fitz  # PyMuPDF
import streamlit as st
import re
from typing import List, Dict, Tuple
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import Config

def extract_structured_text(pdf_file) -> Tuple[List[Dict], int]:
    """
    Extract text and identify headings from a PDF to preserve its structure.
    
    Args:
        pdf_file: Uploaded PDF file object
        
    Returns:
        Tuple[List[Dict], int]: List of structured text blocks and total pages
    """
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    structured_text = []
    current_heading = Config.DEFAULT_HEADING
    total_pages = len(doc)
    
    if total_pages == 0:
        st.error("❌ PDF appears to be empty or corrupted.")
        return [], 0
    
    # Regex to identify headings
    heading_regex = re.compile(Config.HEADING_REGEX_PATTERN)
    progress_bar = st.progress(0, text="Extracting document structure...")
    total_text_extracted = ""

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        total_text_extracted += text
        lines = text.split('\n')
        page_content_buffer = ""

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:  # Skip empty lines
                continue
                
            match = heading_regex.match(line_stripped)
            if match:
                # Save previous buffer if it has content
                if page_content_buffer.strip():
                    structured_text.append({
                        "page_number": page_num + 1,
                        "heading": current_heading,
                        "content": page_content_buffer.strip()
                    })
                
                # Update to new heading
                current_heading = line_stripped
                page_content_buffer = ""
            else:
                page_content_buffer += line + "\n"
        
        # Add remaining text from the page
        if page_content_buffer.strip():
            structured_text.append({
                "page_number": page_num + 1,
                "heading": current_heading,
                "content": page_content_buffer.strip()
            })
        
        progress_bar.progress((page_num + 1) / total_pages)

    progress_bar.empty()
    doc.close()
    
    # Validate extracted text
    if not total_text_extracted.strip():
        st.error("❌ No readable text found in the PDF. The PDF might be image-based or corrupted.")
        return [], total_pages
    
    if not structured_text:
        st.warning("⚠️ No structured content found. Creating a single section with all content.")
        structured_text = [{
            "page_number": 1,
            "heading": "Document Content",
            "content": total_text_extracted.strip()
        }]
    
    return structured_text, total_pages

def create_metadata_chunks(structured_text: List[Dict], splitter: RecursiveCharacterTextSplitter) -> List[Dict]:
    """
    Create chunks from structured text, ensuring each chunk has metadata.
    
    Args:
        structured_text (List[Dict]): List of structured text blocks
        splitter (RecursiveCharacterTextSplitter): Text splitter instance
        
    Returns:
        List[Dict]: List of chunks with metadata
    """
    chunks_with_metadata = []
    
    for block in structured_text:
        if not block['content'].strip():  # Skip empty content blocks
            continue
            
        text_chunks = splitter.split_text(block['content'])
        for chunk in text_chunks:
            if chunk.strip():  # Only add non-empty chunks
                chunks_with_metadata.append({
                    "text": chunk.strip(),
                    "page_number": block['page_number'],
                    "heading": block['heading']
                })
    
    return chunks_with_metadata

def validate_pdf_content(structured_text: List[Dict], chunks: List[Dict]) -> Tuple[bool, str]:
    """
    Validate that PDF processing was successful.
    
    Args:
        structured_text (List[Dict]): Structured text blocks
        chunks (List[Dict]): Text chunks with metadata
        
    Returns:
        Tuple[bool, str]: Success status and message
    """
    if not structured_text:
        return False, "No structured text could be extracted from the PDF"
    
    if not chunks:
        return False, "No valid text chunks could be created from the PDF content"
    
    # Check if chunks have meaningful content
    meaningful_chunks = [chunk for chunk in chunks if len(chunk['text'].strip()) > 10]
    if not meaningful_chunks:
        return False, "PDF content appears to be too short or fragmented"
    
    return True, f"Successfully processed PDF with {len(chunks)} chunks"

class PDFProcessor:
    """
    Class to handle PDF processing operations.
    """
    
    def __init__(self, text_splitter: RecursiveCharacterTextSplitter):
        self.text_splitter = text_splitter
    
    def process_pdf(self, pdf_file) -> Tuple[bool, Dict]:
        """
        Complete PDF processing pipeline.
        
        Args:
            pdf_file: Uploaded PDF file object
            
        Returns:
            Tuple[bool, Dict]: Success status and processing results
        """
        try:
            # Extract structured text
            structured_text, total_pages = extract_structured_text(pdf_file)
            
            if not structured_text or total_pages == 0:
                return False, {"error": "Failed to extract content from PDF"}
            
            # Create chunks
            chunks = create_metadata_chunks(structured_text, self.text_splitter)
            
            # Validate processing
            is_valid, message = validate_pdf_content(structured_text, chunks)
            
            if not is_valid:
                return False, {"error": message}
            
            return True, {
                "structured_text": structured_text,
                "chunks": chunks,
                "total_pages": total_pages,
                "total_chunks": len(chunks),
                "message": message
            }
            
        except Exception as e:
            return False, {"error": f"PDF processing failed: {str(e)}"}
    
    def get_document_structure(self, chunks: List[Dict]) -> Dict:
        """
        Extract document structure information for display.
        
        Args:
            chunks (List[Dict]): Text chunks with metadata
            
        Returns:
            Dict: Document structure information
        """
        if not chunks:
            return {"headings": [], "pages": 0, "total_chunks": 0}
        
        unique_headings = sorted(
            list(set(chunk['heading'] for chunk in chunks)), 
            key=lambda x: (len(x), x)
        )
        
        max_page = max(chunk['page_number'] for chunk in chunks)
        
        return {
            "headings": unique_headings,
            "pages": max_page,
            "total_chunks": len(chunks),
            "chunks_by_heading": {
                heading: len([c for c in chunks if c['heading'] == heading])
                for heading in unique_headings
            }
        }