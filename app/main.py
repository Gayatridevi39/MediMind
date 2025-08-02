import streamlit as st
import os
import io
from dotenv import load_dotenv
from streamlit_star_rating import st_star_rating

# Load environment variables early
load_dotenv()

# Basic imports for UI
from pages import about

# Import performance utilities
import sys
sys.path.append('utils')
from utils.performance import (
    MemoryOptimizer, 
    PerformanceMonitor, 
    AsyncOperations, 
    CacheOptimizer,
    monitor_performance
)

# Lazy import functions for heavy dependencies
@st.cache_resource
def get_llm():
    """Lazy load LangChain and Gemini components"""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.runnables import RunnableSequence
        
        api_key = os.getenv("GEMINI_KEY") or st.secrets.get("GEMINI_KEY")
        if not api_key:
            raise ValueError("GEMINI_KEY not found in .env file")
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key
        )
        
        # Prompt templates
        summary_prompt = PromptTemplate.from_template("""
{{
  "role": "You are the best medical expert in the world with 20 years of experience.",
  "task": "Analyze and summarize the entire medical report with key findings.",
  "who_for": "Non-medico individuals, doctors, freshers.",
  "emotion": "Friendly, mature, and caring.",
  "report_text": "{report_text}",
  "output": "Provide a 4-line summary. If needed, add a key findings table."
}}
""")
        
        qa_prompt = PromptTemplate.from_template("""
    {{
"role" : "You are the best medical expert and top most professor in the world having 20 years of experience",
"task" : "Answer the user questions with clarity and accuracy",
"resources": "Based on the medical report uploaded by the user",
"who_for": "Non-medico individuals, doctors, freshers, illiterate.",
"emotion": "Friendly, mature, and caring.",
"question": "{question}",
"medical_report": "{report_text}",
"output" : "Provide a 2-line answer. If needed elaborate further for complex questions"
}}"""
)
        
        summary_chain = summary_prompt | llm
        qa_chain = qa_prompt | llm
        
        return summary_chain, qa_chain
    except Exception as e:
        st.error(f"Error loading Gemini API: {e}")
        st.stop()

@st.cache_resource
def get_translator():
    """Lazy load translation functionality"""
    from deep_translator import GoogleTranslator
    return GoogleTranslator

# ---------------- Streamlit App Configuration ---------------- #

st.set_page_config(
    page_title="Medical Report Summarizer",
    page_icon="app/assets/logo.png",
    initial_sidebar_state="expanded",
    layout="wide"
)

# Performance CSS optimizations
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] > ul {
        display: none;
    }
    
    /* Optimize loading animations */
    .stSpinner > div {
        border-width: 2px;
    }
    
    /* Reduce visual overhead */
    .main > div {
        padding-top: 2rem;
    }
    
    /* Optimize button styling */
    .stButton > button {
        transition: none;
    }
    </style>
""", unsafe_allow_html=True)

# App header with performance monitoring
@monitor_performance("header_render")
def render_header():
    st.logo("app/assets/logo.png", size="large")
    with st.sidebar:
        st.sidebar.title("📋 Menu")
        st.page_link("main.py", label="Home", icon="🏠")
        st.page_link("pages/about.py", label="About", icon="ℹ️")
        st.page_link("https://www.google.co.in/", label="Google", icon="🌎")
        
        # Performance monitoring section (expandable)
        with st.expander("⚡ Performance Monitor", expanded=False):
            metrics = PerformanceMonitor.get_performance_summary()
            if metrics:
                for func_name, data in metrics.items():
                    st.metric(
                        f"{func_name}", 
                        f"{data['execution_time']:.2f}s",
                        delta=None
                    )
            else:
                st.info("No performance data yet")
    
    st.title("🩺 Medical Report Summarizer & Interpreter")
    st.markdown("A smart AI assistant to help you understand your medical reports in simple language.")

render_header()

# Memory optimization - clear cache periodically
if 'cache_clear_counter' not in st.session_state:
    st.session_state['cache_clear_counter'] = 0

st.session_state['cache_clear_counter'] += 1
if st.session_state['cache_clear_counter'] % 10 == 0:  # Clear every 10 interactions
    MemoryOptimizer.force_garbage_collection()

st.markdown("---")

left_col, middle_col, right_col = st.columns([2,1,2])


with left_col:
    st.subheader("📤 Upload & Extract Medical Report")
    
    # Optimized text extraction with performance monitoring
    @PerformanceMonitor.timer
    @st.cache_data(show_spinner=False, max_entries=5, ttl=1800)
    def extract_text_optimized(file_bytes, file_name):
        """Optimized text extraction with memory management"""
        try:
            file_extension = file_name.split('.')[-1].lower()
            
            # Use the optimized text extraction from performance utilities
            result = CacheOptimizer.optimized_text_extraction(file_bytes, file_extension)
            
            # Force garbage collection for large files
            if len(file_bytes) > 1024 * 1024:  # 1MB
                MemoryOptimizer.force_garbage_collection()
            
            return result if result else "Error: Could not extract text from file"
        except Exception as e:
            return f"Error extracting text: {e}"
    
    # File upload with progress indication
    uploaded_file = st.file_uploader(
        "Upload a medical report (PDF, CSV, TXT, DATA)", 
        type=['pdf', 'data', 'txt', 'csv'],
        help="Supported formats: PDF, CSV, TXT, DATA files up to 50MB"
    )
    
    if uploaded_file:
        # Show file info
        st.info(f"📁 **File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        with st.spinner("🔄 Processing file..."):
            file_bytes = uploaded_file.getvalue()
            extracted = extract_text_optimized(file_bytes, uploaded_file.name)
    
        if extracted and not extracted.startswith("Error"):
            st.session_state['extracted_text'] = extracted
            st.success("✅ Text extracted successfully.")
            
            # Show preview with character limit for performance
            preview_text = extracted[:1000] + "..." if len(extracted) > 1000 else extracted
            st.text_area("📄 Raw Extracted Text (Preview)", value=preview_text, height=200)
            
            # Show full text toggle
            if len(extracted) > 1000:
                if st.button("📜 Show Full Text"):
                    st.text_area("📄 Full Extracted Text", value=extracted, height=400)
        else:
            st.error(extracted)

with middle_col:
    st.write()

# Q&A Section with performance optimization
with right_col:
# st.markdown("---")
    st.subheader("🧠 AI-Powered Medical Report Q&A")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        qa = st.text_input("Enter your question about your report")
    with col2:
        st.write("")  # Spacing
        clear_qa = st.button("Clear", key="clear_qa")
    
    if clear_qa:
        st.rerun()
    
    @monitor_performance("qa_generation")
    def generate_answer(question, report_text):
        """Generate answer with performance monitoring"""
        summary_chain, qa_chain = get_llm()
        return qa_chain.invoke(report_text=report_text, question=question)
    
    if st.button("Generate Answer", type="primary") and qa:
        if "extracted_text" in st.session_state:
            with st.spinner("🧠 Analyzing and answering..."):
                try:
                    answer_result = generate_answer({"report_text" : st.session_state["extracted_text"],
                            "question" : qa})
                    answer = answer_result.content
                    st.subheader("🔎 Answer:")
                    st.markdown(answer)
                    
                    # Store in session for reference
                    if 'qa_history' not in st.session_state:
                        st.session_state['qa_history'] = []
                    st.session_state['qa_history'].append({
                        'question': qa,
                        'answer': answer
                    })
                    
                except Exception as e:
                    st.error(f"Failed to generate answer: {e}")
        else:
            st.warning("Please upload and extract a report first.")

# Summarization Section with optimization
with left_col:
    st.markdown("---")
    st.subheader("🧾 Summarize Report")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        languages = ["English", "Hindi", "Telugu", "Spanish", "French", "German", "Chinese"]
        selected_language = st.selectbox("Select Output Language", languages)
    
    with col2:
        st.write("")  # Spacing
        include_translation = st.checkbox("Auto-translate", value=(selected_language != "English"))
    
    @monitor_performance("summary_generation")
    def generate_summary(report_text, language):
        """Generate summary with performance monitoring"""
        summary_chain, _ = get_llm()
        summary_result = summary_chain.invoke({"report_text":st.session_state["extracted_text"]})
        summary = summary_result.content
        
        if language != "English" and include_translation:
            GoogleTranslator = get_translator()
            translated_summary = GoogleTranslator(source='auto', target=language.lower()).translate(summary)
            return summary, translated_summary
        
        return summary, None
    
    if st.button("Get Report Summary", type="primary"):
        if "extracted_text" in st.session_state and st.session_state["extracted_text"].strip():
            with st.spinner("📝 Generating summary..."):
                try:
                    summary, translated_summary = generate_summary(
                        st.session_state["extracted_text"], 
                        selected_language
                    )
                    st.session_state["summary"] = summary
        
                    if translated_summary:
                        st.subheader(f"📝 Summary in {selected_language}:")
                        st.write(translated_summary)
                        st.download_button(
                            f"Download summary in {selected_language}", 
                            translated_summary,
                            file_name=f"medical_summary_{selected_language.lower()}.txt"
                        )
                    else:
                        st.subheader("📝 AI Summary:")
                        st.write(summary)
                        st.download_button(
                            "Download summary", 
                            summary,
                            file_name="medical_summary.txt"
                        ) 
                except Exception as e:
                    st.error(f"Summary generation failed: {e}")
        else:
            st.warning("Please upload and extract a report first.")

# --------- PubMed Article Search with batch processing---------
with right_col:
    
    st.markdown("---")        
    st.subheader("🔍 Find Research Articles about your condition")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        query = st.text_input("Enter medical topic or condition", placeholder="e.g. diabetes, cancer, COVID-19")
    with col2:
        options = list(range(1, 11))
        choice = st.selectbox("Number of articles", options, index=4)
    
    # Enhanced search with batch processing
    @monitor_performance("pubmed_search")
    @st.cache_data(show_spinner=False, ttl=3600)
    def search_pubmed_optimized(query: str, max_results: int):
        """Optimized PubMed search with better error handling"""
        try:
            import requests
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"  # Get most relevant results first
            }
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            return data.get("esearchresult", {}).get("idlist", [])
        except Exception as e:
            st.error(f"❌ Error fetching PubMed IDs: {e}")
            return []
    
    @st.cache_data(show_spinner=False, ttl=3600)
    def fetch_articles_optimized(pmid_list):
        """Optimized article fetching"""
        try:
            import requests
            if not pmid_list:
                return ""
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            ids = ",".join(pmid_list[:10])  # Limit to 10 articles max
            params = {
                "db": "pubmed",
                "id": ids,
                "retmode": "xml"
            }
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            return response.text 
        except Exception as e:
            st.error(f"❌ Error fetching article details: {e}")
            return ""
    
    def parse_articles_optimized(xml_data):
        """Optimized XML parsing"""
        import xml.etree.ElementTree as ET
        articles = []
        try:
            root = ET.fromstring(xml_data)
            for article in root.findall(".//PubmedArticle"):
                title = article.findtext(".//ArticleTitle", default="No title")
                abstract = article.findtext(".//Abstract/AbstractText", default="No abstract available")
                pmid = article.findtext(".//PMID")
                
                # Truncate long abstracts for better performance
                if len(abstract) > 500:
                    abstract = abstract[:500] + "..."
                
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "#"
                articles.append({
                    "title": title,
                    "abstract": abstract,
                    "url": url,
                    "pmid": pmid
                })
        except Exception as e:
            st.error(f"❌ Error parsing articles: {e}")
        return articles
    
    if st.button("Search Articles", type="primary"):
        if query.strip():
            with st.spinner("🔍 Searching PubMed database..."):
                pmids = search_pubmed_optimized(query, choice)
                if not pmids:
                    st.warning("⚠️ No results found for the query.")
                else:
                    xml_data = fetch_articles_optimized(pmids)
                    
                    if xml_data:
                        articles = parse_articles_optimized(xml_data)
                    
                        if articles:
                            st.success(f"✅ Found {len(articles)} articles.")
                            
                            # Display articles in a more organized way
                            for i, art in enumerate(articles, 1):
                                with st.expander(f"📄 Article {i}: {art['title'][:100]}{'...' if len(art['title']) > 100 else ''}"):
                                    st.write(f"**Abstract:** {art['abstract']}")
                                    st.markdown(f"🔗 [Read on PubMed]({art['url']})")
                                    if art['pmid']:
                                        st.caption(f"PMID: {art['pmid']}")
                        else:
                            st.warning("⚠️ No articles found for the query.")
                    else:
                        st.warning("⚠️ Failed to fetch article details.")
        else:
            st.warning("⚠️ Please enter a valid search term.")

# Feedback
st.markdown("---")
col11, col12, col13 = st.columns([2,2,1])
with col12:
    st.markdown("### Your opinion matters! Help us enhance your journey")
    rating = st_star_rating("", maxValue=5, defaultValue=0, key="rating4", emoticons=True, resetButton=True)
    
    if rating:
        st.markdown("Thankyou for your valuable feedback! It helps us grow.")
