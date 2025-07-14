import streamlit as st
import fitz  
from dotenv import load_dotenv
import pandas as pd
import os
import io
from pages import about
import requests
from deep_translator import GoogleTranslator



# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


# Load environment variables
load_dotenv()

try:
    api_key = os.getenv("GEMINI_KEY") or st.secrets.get("GEMINI_KEY")
    if not api_key:
        raise ValueError("GEMINI_KEY not found in .env file")
    llm = ChatGoogleGenerativeAI(
              model="gemini-2.0-flash",
              google_api_key= api_key
    )
except Exception as e:
    st.error(f"Error loading Gemini API: {e}")
    st.stop()

# Prompt for medical report summarization
summary_prompt = PromptTemplate(
    input_variables=["report_text"],
    template="""
You are a medical AI expert. Summarize the following medical report clearly and concisely for a doctor:

Medical Report:
{report_text}

Summary:
"""
)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt)

# Prompt for medical Q&A
qa_prompt = PromptTemplate(
    input_variables=["report_text", "question"],
    template="""
You are a medical expert AI. Based only on the given medical report, answer the question accurately.

Medical Report:
{report_text}

Question: {question}

Answer:
"""
)
qa_chain = LLMChain(llm=llm, prompt=qa_prompt)




# ---------------- Streamlit App ---------------- #

#page title
st.set_page_config(
    page_title="Medical Report Summarizer",
    page_icon="app/assets.logo.png",
    initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] > ul {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)


st.logo("app/assets/logo.png", size="large")
with st.sidebar:
    st.sidebar.title("📋 Menu")
    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/about.py", label="About", icon="ℹ️")
    st.page_link("https://www.google.co.in/", label="Google", icon="🌎")
    


st.title("🩺 Medical Report Summarizer & Interpreter")
st.markdown("A smart AI assistant to help you understand your medical reports in simple language.")

st.markdown("---")
st.subheader("📤 Upload & Extract Medical Report")

# Text extraction function
@st.cache_data(show_spinner=False)
def extract_text(file_bytes, file_name):
    try:
        if file_name.endswith(".pdf"):
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            return "".join([page.get_text() for page in doc])
        
        elif file_name.endswith((".txt", ".data")):
            return file_bytes.decode("utf-8")
    
        elif file_name.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(file_bytes))
            return df.to_string(index=False)
        
        else:
            return "!!! Unsupported file type. Please upload a valid file type (PDF, CSV, TXT, DATA)"
    except Exception as e:
        return f"Error extracting text: {e}"

# Upload file
uploaded_file = st.file_uploader("Upload a medical report of type : PDF, CSV, DATA, TXT", type=['pdf', 'data', 'txt', 'csv'])


# Extract text after upload
if uploaded_file :
    file_bytes = uploaded_file.getvalue()
    extracted = extract_text(file_bytes, uploaded_file.name)

    if extracted.strip(): 
        st.session_state['extracted_text'] = extracted
        st.success("✅ Text extracted successfully.")
        st.text_area("📄 Raw Extracted Text", value=extracted, height=300)
    else:
        st.error(extracted)
    


# ----- Q&A Section -----

st.markdown("---")
st.subheader("🧠 AI-Powered Medical Report Q&A")

qa = st.text_input("Enter your question about your report")

if st.button("Generate Answer") and qa:
    if "extracted_text" in st.session_state:
        with st.spinner("Answering..."):
            try:
                answer = qa_chain.run(
                    report_text=st.session_state["extracted_text"],
                    question=qa
                )
                st.subheader("🔎 Answer:")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Failed to generate answer: {e}")
    else:
        st.warning("Please upload and extract a report first.")


# --- Summarization Section ---

st.markdown("---")
st.subheader("🧾 Summarize Report")

languages = ["English", "Hindi", "Telugu", "Spanish", "French", "German", "Chinese"]
selected_language = st.selectbox("Select Output Language", languages)

if st.button("Get Report Summary"):
    if "extracted_text" in st.session_state and st.session_state["extracted_text"].strip():
        with st.spinner("Summarizing..."):
            try:
                summary = summary_chain.run(report_text=st.session_state["extracted_text"])
                st.session_state["summary"] = summary
    
                if selected_language != "English":
                   st.subheader(f"📝 Summary in {selected_language}:")
                   translated_summary = GoogleTranslator(source='auto', target=selected_language.lower()).translate(summary)
                   st.write(translated_summary)
                   st.download_button(f"Download summary in {selected_language}", translated_summary)
                else:
                    st.subheader("📝 AI Summary:")
                    st.write(summary)
                    st.download_button("Download summary", summary) 
            except Exception as e:
                st.error(f"Summary generation failed: {e}")
    else:
        st.warning("Please upload and extract a report first.")
        
st.markdown("---")        

# ----- Pubmed Article Search -----
        
st.subheader("🔍 Find Reasearch Articles about your condition")

query = st.text_input("Enter medical topic or condition", placeholder="e.g. diabetes, cancer, COVID-19")
options = list(range(1, 11))
choice = st.selectbox("Pick how many articles to show", options, index=4)

# ----Search for related articles ------

@st.cache_data(show_spinner=False)
def search_pubmed(query: str, max_results: int):
    try:
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            "db" : "pubmed",
            "term" : query,
            "retmax" : max_results,
            "retmode" : "json"
        }
        response  = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("esearchresult", {}).get("idlist", [])
    except Exception as e:
        st.error(f"❌ Error fetching PubMed IDs: {e}")
        return []

@st.cache_data(show_spinner=False)
def fetch_articles(pmid_list):
    try:
        if not pmid_list:
            return ""
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        ids = ",".join(pmid_list)
        params = {
            "db": "pubmed",
            "id": ids,
            "retmode": "xml"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.text 
    except Exception as e:
        st.error(f"❌ Error fetching article details: {e}")
        return ""

import xml.etree.ElementTree as ET

def parse_articles(xml_data):
    articles = []
    try:
        root = ET.fromstring(xml_data)
        for article in root.findall(".//PubmedArticle"):
            title = article.findtext(".//ArticleTitle", default="No title")
            abstract = article.findtext(".//Abstract/AbstractText", default="No abstract available")
            pmid = article.findtext(".//PMID")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "#"
            articles.append({
                "title": title,
                "abstract": abstract,
                "url": url
            })
    except Exception as e:
        st.error(f"❌ Error parsing articles: {e}")
    return articles


if st.button("Search Articles"):
    if query.strip():
        with st.spinner("Searching PubMed...."):
            st.write("🔍 Search term:", query)
            pmids = search_pubmed(query, choice)
            if not pmids:
                st.warning("⚠️ No results found for the query.")
            else:
                xml_data = fetch_articles(pmids)
                
                articles = parse_articles(xml_data)
            
                if articles:
                    st.success(f"✅ Found {len(articles)} articles.")
                    for art in articles:
                        st.subheader(art["title"])
                        st.write(art["abstract"])
                        st.markdown(f"[Read on PubMed] ({art['url']})")
                        st.markdown("---")
                else:
                    st.warning("⚠️ No articles found for the query.")
    else:
        st.warning("⚠️ Please enter a valid search term.")
