"""
Vector Store module for DELINEATE AND DECIPHER application.
Handles FAISS vector database operations and embedding management.
"""

import faiss
import numpy as np
import streamlit as st
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer

def create_vector_store(chunks: List[Dict], embeddings_model: SentenceTransformer) -> Optional[faiss.IndexFlatL2]:
    """
    Create a FAISS vector store from text chunks.
    
    Args:
        chunks (List[Dict]): List of text chunks with metadata
        embeddings_model (SentenceTransformer): Embedding model instance
        
    Returns:
        Optional[faiss.IndexFlatL2]: FAISS index or None if creation fails
    """
    chunk_texts = [chunk['text'] for chunk in chunks if chunk['text'].strip()]
    
    if not chunk_texts:
        st.error("❌ No valid text chunks found in the PDF. Please check if the PDF contains readable text.")
        return None
    
    st.info(f"Creating embeddings for {len(chunk_texts)} chunks...")
    
    try:
        embeddings_array = embeddings_model.encode(chunk_texts, show_progress_bar=True)
        
        # Ensure embeddings_array is 2D
        if embeddings_array.ndim == 1:
            embeddings_array = embeddings_array.reshape(1, -1)
        
        if embeddings_array.shape[0] == 0:
            st.error("❌ Failed to create embeddings. Please check the PDF content.")
            return None
            
        index = faiss.IndexFlatL2(embeddings_array.shape[1])
        index.add(np.array(embeddings_array).astype('float32'))
        return index
        
    except Exception as e:
        st.error(f"❌ Error creating vector store: {str(e)}")
        return None

def search_vector_store(query: str, index: faiss.IndexFlatL2, chunks: List[Dict], 
                       embeddings_model: SentenceTransformer, top_k: int = 20) -> List[Dict]:
    """
    Search the vector store for relevant chunks.
    
    Args:
        query (str): Search query
        index (faiss.IndexFlatL2): FAISS index
        chunks (List[Dict]): Original chunks with metadata
        embeddings_model (SentenceTransformer): Embedding model
        top_k (int): Number of results to return
        
    Returns:
        List[Dict]: Retrieved chunks with similarity scores
    """
    try:
        query_embedding = embeddings_model.encode([query]).astype('float32')
        distances, indices = index.search(query_embedding, top_k)
        
        retrieved_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx < len(chunks):  # Ensure valid index
                chunk = chunks[idx].copy()
                chunk['similarity_score'] = float(distances[0][i])
                retrieved_chunks.append(chunk)
        
        return retrieved_chunks
        
    except Exception as e:
        st.error(f"❌ Error searching vector store: {str(e)}")
        return []

def get_vector_store_stats(index: Optional[faiss.IndexFlatL2], chunks: List[Dict]) -> Dict:
    """
    Get statistics about the vector store.
    
    Args:
        index (Optional[faiss.IndexFlatL2]): FAISS index
        chunks (List[Dict]): Text chunks
        
    Returns:
        Dict: Vector store statistics
    """
    if not index:
        return {"status": "not_created", "total_vectors": 0, "dimension": 0}
    
    return {
        "status": "created",
        "total_vectors": index.ntotal,
        "dimension": index.d,
        "total_chunks": len(chunks),
        "index_type": "IndexFlatL2"
    }

class VectorStoreManager:
    """
    Manager class for FAISS vector store operations.
    """
    
    def __init__(self, embeddings_model: SentenceTransformer):
        self.embeddings_model = embeddings_model
        self.index = None
        self.chunks = None
    
    def create_index(self, chunks: List[Dict]) -> bool:
        """
        Create FAISS index from chunks.
        
        Args:
            chunks (List[Dict]): Text chunks with metadata
            
        Returns:
            bool: Success status
        """
        self.index = create_vector_store(chunks, self.embeddings_model)
        if self.index:
            self.chunks = chunks
            return True
        return False
    
    def search(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Search the vector store.
        
        Args:
            query (str): Search query
            top_k (int): Number of results to return
            
        Returns:
            List[Dict]: Retrieved chunks
        """
        if not self.index or not self.chunks:
            return []
        
        return search_vector_store(query, self.index, self.chunks, self.embeddings_model, top_k)
    
    def get_stats(self) -> Dict:
        """Get vector store statistics."""
        return get_vector_store_stats(self.index, self.chunks or [])
    
    def reset(self):
        """Reset the vector store."""
        self.index = None
        self.chunks = None
    
    def is_ready(self) -> bool:
        """Check if vector store is ready for search."""
        return self.index is not None and self.chunks is not None

def optimize_index_for_large_collections(chunks: List[Dict], embeddings_model: SentenceTransformer, 
                                       nlist: int = 100) -> Optional[faiss.IndexIVFFlat]:
    """
    Create an optimized FAISS index for large document collections.
    
    Args:
        chunks (List[Dict]): Text chunks with metadata
        embeddings_model (SentenceTransformer): Embedding model
        nlist (int): Number of clusters for IVF index
        
    Returns:
        Optional[faiss.IndexIVFFlat]: Optimized FAISS index or None
    """
    chunk_texts = [chunk['text'] for chunk in chunks if chunk['text'].strip()]
    
    if len(chunk_texts) < 1000:  # Only optimize for large collections
        return None
    
    try:
        st.info("Creating optimized index for large collection...")
        embeddings_array = embeddings_model.encode(chunk_texts, show_progress_bar=True)
        
        # Create IVF index for faster search on large collections
        quantizer = faiss.IndexFlatL2(embeddings_array.shape[1])
        index = faiss.IndexIVFFlat(quantizer, embeddings_array.shape[1], nlist)
        
        # Train the index
        index.train(embeddings_array.astype('float32'))
        index.add(embeddings_array.astype('float32'))
        
        # Set search parameters
        index.nprobe = 10  # Number of clusters to search
        
        return index
        
    except Exception as e:
        st.error(f"❌ Error creating optimized index: {str(e)}")
        return None