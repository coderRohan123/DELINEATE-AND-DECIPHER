"""
Advanced Retrieval module for DELINEATE AND DECIPHER application.
Handles hybrid retrieval combining structural and semantic search with re-ranking.
"""

import re
import streamlit as st
from typing import List, Dict
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from config import Config

def structural_search(query: str, chunks: List[Dict]) -> List[Dict]:
    """
    Perform structural search by matching query with document headings.
    
    Args:
        query (str): User query
        chunks (List[Dict]): Text chunks with metadata
        
    Returns:
        List[Dict]: Chunks from matching structural sections
    """
    unique_headings = sorted(
        list(set(chunk['heading'] for chunk in chunks)), 
        key=lambda x: (len(x), x)
    )
    
    structural_results = []
    
    for heading in unique_headings:
        # Clean heading by removing numbering patterns
        clean_heading = re.sub(r"^(CHAPTER \d+|(\d{1,2}(\.\d{1,2})*))\s+", "", heading).lower()
        
        # Check if query matches the heading
        if clean_heading in query.lower():
            st.success(f"🎯 Direct hit! Found matching section: **{heading}**")
            matching_chunks = [chunk for chunk in chunks if chunk['heading'] == heading]
            structural_results.extend(matching_chunks)
    
    return structural_results

def semantic_search(query: str, index: faiss.IndexFlatL2, chunks: List[Dict], 
                   embeddings_model: SentenceTransformer, top_k: int = 20) -> List[Dict]:
    """
    Perform semantic search using vector similarity.
    
    Args:
        query (str): User query
        index (faiss.IndexFlatL2): FAISS index
        chunks (List[Dict]): Text chunks with metadata
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
            if idx < len(chunks):
                chunk = chunks[idx].copy()
                chunk['similarity_score'] = float(distances[0][i])
                retrieved_chunks.append(chunk)
        
        return retrieved_chunks
        
    except Exception as e:
        st.error(f"❌ Error in semantic search: {str(e)}")
        return []

def rerank_results(query: str, chunks: List[Dict], reranker: CrossEncoder) -> List[Dict]:
    """
    Re-rank search results using cross-encoder model.
    
    Args:
        query (str): User query
        chunks (List[Dict]): Retrieved chunks
        reranker (CrossEncoder): Cross-encoder model for re-ranking
        
    Returns:
        List[Dict]: Re-ranked chunks with scores
    """
    if not chunks:
        return []
    
    try:
        # Prepare pairs for re-ranking
        rerank_pairs = [[query, chunk['text']] for chunk in chunks]
        scores = reranker.predict(rerank_pairs)
        
        # Add re-ranking scores to chunks
        for i, chunk in enumerate(chunks):
            chunk['rerank_score'] = float(scores[i])
        
        # Sort by re-ranking score (higher is better)
        reranked_chunks = sorted(chunks, key=lambda x: x['rerank_score'], reverse=True)
        
        return reranked_chunks
        
    except Exception as e:
        st.error(f"❌ Error in re-ranking: {str(e)}")
        return chunks

def advanced_retrieval(query: str, index: faiss.IndexFlatL2, chunks: List[Dict], 
                      embeddings_model: SentenceTransformer, reranker: CrossEncoder) -> List[Dict]:
    """
    Perform hybrid retrieval combining structural and semantic search with re-ranking.
    
    Args:
        query (str): User query
        index (faiss.IndexFlatL2): FAISS index
        chunks (List[Dict]): Text chunks with metadata
        embeddings_model (SentenceTransformer): Embedding model
        reranker (CrossEncoder): Re-ranking model
        
    Returns:
        List[Dict]: Final retrieved and re-ranked chunks
    """
    # Pass 1: Structural Search
    structural_results = structural_search(query, chunks)
    
    if structural_results:
        # Re-rank structural results
        reranked_chunks = rerank_results(query, structural_results, reranker)
        return reranked_chunks[:Config.STRUCTURAL_SEARCH_TOP_K]
    
    # Pass 2: Semantic Search (Fallback)
    st.info("No direct section match found. Performing semantic search...")
    semantic_results = semantic_search(
        query, index, chunks, embeddings_model, Config.SEMANTIC_SEARCH_TOP_K
    )
    
    if semantic_results:
        # Re-rank semantic results
        reranked_chunks = rerank_results(query, semantic_results, reranker)
        return reranked_chunks[:Config.SEMANTIC_FALLBACK_TOP_K]
    
    return []

def format_context_for_llm(retrieved_chunks: List[Dict]) -> str:
    """
    Format retrieved chunks into context string for LLM.
    
    Args:
        retrieved_chunks (List[Dict]): Retrieved chunks with metadata
        
    Returns:
        str: Formatted context string
    """
    if not retrieved_chunks:
        return "No relevant context found."
    
    context_parts = []
    for chunk in retrieved_chunks:
        context_part = f"--- Context from Page {chunk['page_number']}, Section: {chunk['heading']} ---\n{chunk['text']}"
        context_parts.append(context_part)
    
    return "\n\n".join(context_parts)

def get_search_statistics(retrieved_chunks: List[Dict]) -> Dict:
    """
    Get statistics about the search results.
    
    Args:
        retrieved_chunks (List[Dict]): Retrieved chunks
        
    Returns:
        Dict: Search statistics
    """
    if not retrieved_chunks:
        return {
            "total_chunks": 0,
            "unique_pages": 0,
            "unique_sections": 0,
            "avg_rerank_score": 0,
            "score_range": (0, 0)
        }
    
    unique_pages = len(set(chunk['page_number'] for chunk in retrieved_chunks))
    unique_sections = len(set(chunk['heading'] for chunk in retrieved_chunks))
    
    rerank_scores = [chunk.get('rerank_score', 0) for chunk in retrieved_chunks]
    avg_score = sum(rerank_scores) / len(rerank_scores) if rerank_scores else 0
    score_range = (min(rerank_scores), max(rerank_scores)) if rerank_scores else (0, 0)
    
    return {
        "total_chunks": len(retrieved_chunks),
        "unique_pages": unique_pages,
        "unique_sections": unique_sections,
        "avg_rerank_score": avg_score,
        "score_range": score_range
    }

class AdvancedRetriever:
    """
    Advanced retrieval system combining multiple search strategies.
    """
    
    def __init__(self, embeddings_model: SentenceTransformer, reranker: CrossEncoder):
        self.embeddings_model = embeddings_model
        self.reranker = reranker
    
    def retrieve(self, query: str, index: faiss.IndexFlatL2, chunks: List[Dict]) -> Dict:
        """
        Perform complete retrieval pipeline.
        
        Args:
            query (str): User query
            index (faiss.IndexFlatL2): FAISS index
            chunks (List[Dict]): Text chunks with metadata
            
        Returns:
            Dict: Retrieval results with context and statistics
        """
        try:
            # Perform advanced retrieval
            retrieved_chunks = advanced_retrieval(
                query, index, chunks, self.embeddings_model, self.reranker
            )
            
            # Format context for LLM
            context = format_context_for_llm(retrieved_chunks)
            
            # Get search statistics
            stats = get_search_statistics(retrieved_chunks)
            
            return {
                "success": True,
                "chunks": retrieved_chunks,
                "context": context,
                "statistics": stats,
                "query": query
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "chunks": [],
                "context": "Error occurred during retrieval.",
                "statistics": get_search_statistics([]),
                "query": query
            }
    
    def explain_retrieval_strategy(self, query: str, chunks: List[Dict]) -> str:
        """
        Explain which retrieval strategy will be used for a query.
        
        Args:
            query (str): User query
            chunks (List[Dict]): Text chunks with metadata
            
        Returns:
            str: Explanation of retrieval strategy
        """
        structural_results = structural_search(query, chunks)
        
        if structural_results:
            return f"🎯 **Structural Search**: Query matches document sections directly. Found {len(structural_results)} relevant chunks."
        else:
            return "🔍 **Semantic Search**: No direct section match found. Using vector similarity search with re-ranking."