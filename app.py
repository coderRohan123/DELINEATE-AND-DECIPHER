"""
DELINEATE AND DECIPHER - Modular RAG Application
A RAG-powered AI platform for Research Paper Analysis and Visual Math Problem Solving.
"""

import streamlit as st

# Import modular components
from models import load_embedding_model, load_reranking_model, get_text_splitter, call_groq_api
from pdf_processor import PDFProcessor
from vector_store import VectorStoreManager
from retrieval import AdvancedRetriever
from ui_components import (
    setup_page_config, render_navigation_sidebar, render_sidebar_content,
    render_delineate_sidebar_controls, render_pdf_uploader, render_document_structure,
    render_chat_interface, render_home_content, render_about_content,
    render_decipher_content, UIManager
)
from utils import validate_environment, validate_pdf_file

def process_pdf_pipeline(uploaded_file):
    """Handle PDF processing pipeline."""
    with st.spinner("Processing PDF..."):
        # Initialize components
        text_splitter = get_text_splitter()
        embedding_model = load_embedding_model()
        reranker = load_reranking_model()
        
        # Process PDF
        pdf_processor = PDFProcessor(text_splitter)
        success, results = pdf_processor.process_pdf(uploaded_file)
        
        if not success:
            st.error(f"❌ {results.get('error')}")
            return
        
        # Store results
        st.session_state.chunks = results['chunks']
        st.success(f"✅ Processed {results['total_pages']} pages, {results['total_chunks']} chunks")
        
        # Create vector store
        vector_store = VectorStoreManager(embedding_model)
        if vector_store.create_index(results['chunks']):
            st.session_state.vector_store_manager = vector_store
            st.session_state.retriever = AdvancedRetriever(embedding_model, reranker)
            st.session_state.pdf_processed = True
            st.session_state.messages = []
            st.success("✅ Vector database created")
            st.balloons()

def handle_chat(prompt):
    """Handle chat interaction."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        retriever = st.session_state.retriever
        vector_store = st.session_state.vector_store_manager
        
        retrieval_results = retriever.retrieve(prompt, vector_store.index, vector_store.chunks)
        
        if retrieval_results["success"]:
            response = call_groq_api(prompt, retrieval_results["context"])
            st.markdown(response)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": retrieval_results["chunks"]
            })
        else:
            st.error(f"❌ {retrieval_results['error']}")
    st.rerun()

def main():
    """Main application."""
    setup_page_config()
    
    # Validate environment
    env_valid, issues = validate_environment()
    if not env_valid:
        st.error(f"❌ Environment issues: {', '.join(issues)}")
        st.stop()
    
    UIManager.initialize_session_state()
    
    # Navigation
    choice = render_navigation_sidebar()
    render_sidebar_content(choice)
    
    if choice == "✍️ Delineate":
        render_delineate_sidebar_controls()
        
        st.title("✍️ Delineate: PDF Analysis")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = render_pdf_uploader()
            if uploaded_file:
                is_valid, msg = validate_pdf_file(uploaded_file)
                if not is_valid:
                    st.error(f"❌ {msg}")
                elif st.button("🔄 Process PDF"):
                    process_pdf_pipeline(uploaded_file)
        
        with col2:
            if st.session_state.get("pdf_processed"):
                render_document_structure(st.session_state.chunks)
        
        # Chat interface
        render_chat_interface()
        
        if st.session_state.get('pdf_processed'):
            prompt = st.chat_input("Ask about the PDF...")
            if prompt:
                handle_chat(prompt)
        else:
            st.info("📤 Upload and process a PDF to begin")
    
    elif choice == "🏠 Home":
        render_home_content()
    elif choice == "🔍 Decipher":
        render_decipher_content()
    elif choice == "ℹ️ About":
        render_about_content()

if __name__ == "__main__":
    main()