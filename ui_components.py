"""
UI Components module for DELINEATE AND DECIPHER application.
Contains reusable Streamlit UI components and layout functions.
"""

import streamlit as st
import time
from typing import List, Dict, Optional
from config import Config

def setup_page_config():
    """Set up the Streamlit page configuration."""
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.APP_ICON,
        layout=Config.LAYOUT
    )

def render_app_header():
    """Render the main application header."""
    st.markdown(
        f"""
        <h1 style="text-align: center;">
        {Config.APP_TITLE} <br>
        "A RAG powered AI platform for Research Paper Analysis and Visual Math Problem Solving"
        </h1>
        """, unsafe_allow_html=True
    )

def render_animated_marquee():
    """Render the animated marquee banner."""
    st.markdown(
        """
        <style>
        @keyframes flicker {
            0%, 18%, 22%, 25%, 53%, 57%, 100% {
                opacity: 1;
            }
            20%, 24%, 55% {
                opacity: 0.4;
            }
            21%, 23%, 56% {
                opacity: 0.7;
            }
        }
        .marquee {
            animation: flicker 1.5s infinite;
            font-size: 24px;
            font-weight: bold;
            color: #FFA500; /* Orange color */
        }
        </style>

        <marquee behavior="scroll" direction="left" scrollamount="6">
            <span class="marquee">Delineate and Decipher: Revolutionizing Research and Problem-Solving</span>
        </marquee>
        """,
        unsafe_allow_html=True
    )

def render_navigation_sidebar():
    """
    Render the main navigation sidebar.
    
    Returns:
        str: Selected menu option
    """
    return st.sidebar.selectbox("Navigation", Config.MENU_OPTIONS)

def render_sidebar_content(choice: str):
    """
    Render content in the sidebar based on the selected page.
    
    Args:
        choice (str): Selected menu option
    """
    if choice == "🏠 Home":
        st.sidebar.write("Steps to proceed with your research:")
        st.sidebar.write("1. Upload your research papers.")
        st.sidebar.write("2. Process them to create embeddings.")
        st.sidebar.write("3. Ask any questions or explore the math equation solver.")
        st.sidebar.write("4. Navigate to 'Delineate' for PDF processing or 'Decipher' for visual equation solving.")

    elif choice == "✍️ Delineate":
        st.sidebar.title("How to use Delineate:")
        st.sidebar.write("1. Upload your PDF files.")
        st.sidebar.write("2. Click the 'Process PDF' button.")
        st.sidebar.write("3. Once processed, ask questions related to the content of your papers.")
        st.sidebar.write("4. View document similarity and explore the embedded chunks.")

    elif choice == "🔍 Decipher":
        st.sidebar.title("How to use Decipher:")
        st.sidebar.write("1. Draw or input your math equations in the interface.")
        st.sidebar.write("2. Submit your problem to get solutions.")
        st.sidebar.write("3. Explore the process or steps to reach the answer visually.")

    elif choice == "ℹ️ About":
        st.sidebar.write("About this project:")
        st.sidebar.write("Developed for PhD-level research assistance.")
        st.sidebar.write("Powered by GPT-OSS-20B and FAISS for precise academic insights.")

def render_delineate_sidebar_controls():
    """Render the control buttons in the sidebar for Delineate section."""
    if st.session_state.get("pdf_processed"):
        st.sidebar.markdown("---")
        st.sidebar.header("🔧 Controls")
        
        # Clear Chat button
        if st.sidebar.button("💬 Clear Chat", help="Clear only the conversation history"):
            st.session_state.messages = []
            st.success("✅ Chat history cleared!")
            st.rerun()
        
        # Reset All Data button  
        if st.sidebar.button("🗑️ Reset All Data", help="Clear all data including uploaded PDF, embeddings, and chat history"):
            reset_all_application_data()

def reset_all_application_data():
    """Reset all application data including uploaded PDFs and session state."""
    # Get current key before clearing session state
    current_key = st.session_state.get('file_uploader_key', 'file_uploader_0')
    key_num = int(current_key.split('_')[-1]) if '_' in current_key else 0
    
    # Clear all session state (PDF cache, embeddings, conversations, everything)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    # Reset file uploader by changing its key (this clears the uploaded PDF)
    st.session_state.file_uploader_key = f'file_uploader_{key_num + 1}'
    
    st.success("✅ All data cleared including uploaded PDF, embeddings, and chat history!")
    st.info("🔄 Page will refresh to complete reset...")
    time.sleep(1)
    st.rerun()

def render_pdf_uploader():
    """
    Render the PDF file uploader component.
    
    Returns:
        Optional: Uploaded file object or None
    """
    file_uploader_key = st.session_state.get('file_uploader_key', 'file_uploader_0')
    
    return st.file_uploader(
        "Choose a PDF file", 
        type="pdf",
        key=file_uploader_key,
        help="Upload a PDF file to analyze its structure and content"
    )

def render_document_structure(chunks: List[Dict]):
    """
    Render the document structure display in the sidebar.
    
    Args:
        chunks (List[Dict]): Text chunks with metadata
    """
    st.header("🏛️ Document Structure")
    st.info("Ask about these sections directly by name!")
    
    with st.expander("View Extracted Headings", expanded=True):
        unique_headings = sorted(
            list(set(chunk['heading'] for chunk in chunks)), 
            key=lambda x: (len(x), x)
        )
        
        for heading in unique_headings[:10]:  # Show first 10
            st.markdown(f"- `{heading}`")
        
        if len(unique_headings) > 10:
            st.markdown(f"... and {len(unique_headings)-10} more sections")

def render_chat_message(role: str, content: str, sources: Optional[List[Dict]] = None):
    """
    Render a chat message with optional sources.
    
    Args:
        role (str): Message role ('user' or 'assistant')
        content (str): Message content
        sources (Optional[List[Dict]]): Source chunks for citations
    """
    with st.chat_message(role):
        st.markdown(content)
        
        if sources:
            with st.expander("📚 View Sources"):
                for i, source in enumerate(sources):
                    st.info(f"""
                    **Source {i+1}**
                    - **Page:** {source['page_number']}
                    - **Section:** {source['heading']}
                    - **Relevance Score:** {source.get('rerank_score', 'N/A'):.3f}
                    - **Text:** "{source['text'][:250]}..."
                    """)

def render_chat_interface():
    """Render the main chat interface."""
    # Initialize chat messages
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        render_chat_message(
            message["role"], 
            message["content"], 
            message.get("sources")
        )

def render_home_content():
    """Render the home page content."""
    render_app_header()
    render_animated_marquee()
    
    # Display content
    st.markdown(
        """
        ### **Why Use Me?**
        - **Tired of spending hours digging through endless research papers?**
        - **Struggling to quickly locate relevant information from mountains of academic documents?**
        - **Frustrated with complicated math problems that take hours to solve manually?**
        """, unsafe_allow_html=True
    )

    # Try to display image if exists
    try:
        st.image("./assets/pic.jpg",
                 caption="Delineate and Decipher: Revolutionizing Research and Problem-Solving", 
                 width='content')
    except:
        st.info("🖼️ Image placeholder - Add ./assets/pic.jpg for visual enhancement")

    st.markdown(
        """
        **DELINEATE AND DECIPHER** is here to change the way you approach academic research and complex problem-solving. 
        Whether you're a PhD candidate, researcher, or student, this platform is specifically designed to make your life easier and your work more efficient.

        ### **Key Features:**
        - **Delineate**: Seamlessly upload your research papers and let the platform process them into **searchable vector embeddings** with structural awareness. No more endless scrolling—find exactly what you need, when you need it.
        - **Decipher**: Draw or input your toughest math equations, and get **step-by-step visual solutions** powered by cutting-edge AI. It's like having a math tutor in your pocket.

        ### **Advanced Technology Stack:**
        - **GPT-OSS-20B with Reasoning**: Enhanced model with medium reasoning effort for complex academic queries
        - **Structural PDF Analysis**: Understands document structure including chapters, sections, and headings
        - **Cross-Encoder Re-ranking**: Advanced retrieval with semantic re-ranking for precision
        - **FAISS Vector Database**: Lightning-fast similarity search across document collections

        **Ready to explore? Navigate to 'Delineate' to upload your research papers or 'Decipher' for math problem-solving!**
        """
    )

def render_about_content():
    """Render the about page content."""
    st.title("ℹ️ About DELINEATE AND DECIPHER")
    st.markdown("""
        **DELINEATE AND DECIPHER** is an AI-powered platform designed to assist researchers, PhD candidates, and students in analyzing academic papers and solving complex mathematical problems. 

        **What makes it unique:**
        - Uses advanced language models like **GPT-OSS-20B with Reasoning** and **FAISS** for precise academic document retrieval.
        - **Structurally-aware PDF processing** that understands document hierarchy, chapters, and sections.
        - Efficiently processes research papers, turning them into searchable embeddings with metadata preservation.
        - Helps solve math equations with detailed steps, making it perfect for technical problem-solving.
        - **Cross-encoder re-ranking** for enhanced retrieval accuracy beyond simple similarity search.

        **Technology Stack:**
        - **PDF Processing**: PyMuPDF for reliable text extraction
        - **Embeddings**: SentenceTransformer with all-MiniLM-L6-v2 model
        - **Vector Database**: FAISS for lightning-fast similarity search  
        - **Re-ranking**: Cross-encoder for semantic precision
        - **LLM**: GPT-OSS-20B with medium reasoning effort
        - **Framework**: Streamlit for intuitive user interface

        **Future Enhancements:**
        - Incorporating more advanced mathematical capabilities.
        - Improving support for various academic formats.
        - Expanding the visual tools for document analysis.
        - Multi-document analysis and comparison features.
    """)

def render_decipher_content():
    """Render the decipher (math solver) page content."""
    st.title("🔍 Decipher: Solve Math Equations Visually")

    st.markdown("""
        **Decipher** is the section where you can draw mathematical equations, and the platform provides step-by-step solutions using advanced AI visualization. 
        Simply input your equation and get a detailed solution.
    """)

    # Embed the math equation solving tool
    st.components.v1.iframe(Config.MATH_SOLVER_URL, width=800, height=600)

def render_processing_status(processing_results: Dict):
    """
    Render processing status messages.
    
    Args:
        processing_results (Dict): Results from PDF processing
    """
    if processing_results.get("success"):
        st.success(f"✅ {processing_results['message']}")
        if "total_pages" in processing_results:
            st.success(f"✅ Extracted structure from {processing_results['total_pages']} pages.")
        if "total_chunks" in processing_results:
            st.success(f"✅ Created {processing_results['total_chunks']} metadata-rich chunks.")
    else:
        st.error(f"❌ {processing_results.get('error', 'Unknown error occurred')}")

def render_search_statistics(stats: Dict):
    """
    Render search statistics in an info box.
    
    Args:
        stats (Dict): Search statistics
    """
    if stats["total_chunks"] > 0:
        st.info(f"""
        📊 **Search Results**: Found {stats['total_chunks']} relevant chunks across {stats['unique_pages']} pages 
        from {stats['unique_sections']} different sections. 
        Average relevance score: {stats['avg_rerank_score']:.3f}
        """)

class UIManager:
    """Manager class for UI operations and state management."""
    
    @staticmethod
    def initialize_session_state():
        """Initialize all necessary session state variables."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        
        if 'file_uploader_key' not in st.session_state:
            st.session_state.file_uploader_key = 'file_uploader_0'
    
    @staticmethod
    def handle_chat_input(prompt: str, retrieval_results: Dict):
        """
        Handle new chat input and update session state.
        
        Args:
            prompt (str): User's input
            retrieval_results (Dict): Results from retrieval system
        """
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Add assistant response with sources
        st.session_state.messages.append({
            "role": "assistant",
            "content": retrieval_results.get("response", "No response generated"),
            "sources": retrieval_results.get("chunks", [])
        })