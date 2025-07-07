import streamlit as st
import fitz  # PyMuPDF
from dotenv import load_dotenv
import pandas as pd
import os
import io
from pages import about
import requests
from deep_translator import GoogleTranslator

# from transformers import pipeline


# LangChain & Gemini
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize translation pipeline
# translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ROMANCE")

# Load environment variables
load_dotenv()

# Set up Gemini model via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GEMINI_KEY")
)

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

# Upload file
uploaded_file = st.file_uploader("Upload a medical report of type : PDF, CSV, DATA, TXT", type=['pdf', 'data', 'txt', 'csv'])

# Text extraction function
def extract_text(file_bytes, file_name):
    if file_name.endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    
    elif file_name.endswith((".txt", ".data")):
        return file_bytes.decode("utf-8")

    elif file_name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes))
        return df.to_string(index=False)
    

    else:
        return "!!! Unsupported file type. Please upload a valid file type (PDF, CSV, TXT, DATA)"


# Extract text after upload
if uploaded_file and "extracted_text" not in st.session_state:
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name
    text = extract_text(file_bytes, file_name)

    if text.strip():
        st.session_state['extracted_text'] = text
        st.success("✅ Text extracted successfully.")
    else:
        st.warning("⚠️ No readable text found.")

# Show extracted text
if "extracted_text" in st.session_state:
    st.subheader("📄 Raw Extracted Text")
    st.text_area("Extracted Text", value=st.session_state['extracted_text'], height=400)
    


# --- Q&A Section ---
st.markdown("---")
st.subheader("🧠 AI-Powered Medical Report Q&A")

qa = st.text_input("Enter your question")

if st.button("Generate Answer") and qa:
    if "extracted_text" in st.session_state:
        with st.spinner("Answering using LangChain..."):
            answer = qa_chain.run(
                report_text=st.session_state["extracted_text"],
                question=qa
            )
            st.subheader("🔎 Answer:")
            st.markdown(answer)
    else:
        st.warning("Please upload and extract a file first.")


# --- Summarization Section ---
st.markdown("---")
st.subheader("🧾 Summarize Report")

languages = ["English", "Hindi", "Telugu", "Spanish", "French", "German", "Chinese"]
selected_language = st.selectbox("Select Output Language", languages)

if st.button("Get Report Summary"):
    if "extracted_text" in st.session_state and st.session_state["extracted_text"].strip():
        with st.spinner("Generating summary using LangChain..."):
            summary = summary_chain.run(report_text=st.session_state["extracted_text"])
            st.session_state["summary"] = summary

            if selected_language != "English":
               st.subheader(f"📝 Summary in {selected_language}:")
               translated_summary = GoogleTranslator(source='auto', target=selected_language.lower()).translate(summary)
               st.write(translated_summary)
               st.download_button(f"Download summary ({selected_language})", translated_summary)
            else:
                st.subheader("📝 AI Summary:")
                st.write(summary)
                st.download_button("Download summary", summary) 
    else:
        st.warning("Please upload a file and extract text first.")
        
st.markdown("---")        
        
        
st.subheader("🔍 Find Reasearch Articles about your condition")
query = st.text_input("Enter medical topic or condition", placeholder="e.g. diabetes, cancer, COVID-19")
options = list(range(1, 11))
choice = st.selectbox("Pick how many articles to show", options, index=4)

# ----Search for related articles ------
def search_pubmed(query, max_results = choice):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db" : "pubmed",
        "term" : query,
        "retmax" : max_results,
        "retmode" : "json"
    }
    response  = requests.get(url, params=params)
    data = response.json()
    return data["esearchresult"]["idlist"]

def fetch_articles(pmid_list):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    ids = ",".join(pmid_list)
    params = {
        "db": "pubmed",
        "id": ids,
        "retmode": "xml"
    }
    response = requests.get(url, params=params)
    return response.text  # You'll parse this XML

import xml.etree.ElementTree as ET

def parse_articles(xml_data):
    root = ET.fromstring(xml_data)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        try:
            title = article.findtext(".//ArticleTitle")
            abstract = article.findtext(".//Abstract/AbstractText")
            pmid = article.findtext(".//PMID")
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            articles.append({
                "title": title,
                "abstract": abstract,
                "url": url
            })
        except:
            continue
    return articles



if st.button("Search"):
    with st.spinner("Searching PubMed...."):
        pmids = search_pubmed(query)
        xml_data = fetch_articles(pmids)
        articles = parse_articles(xml_data)
        
        if articles:
            st.success(f"Found {len(articles)} articles.")
            for art in articles:
                st.subheader(art["title"])
                st.write(art["abstract"])
                st.markdown(f"[Read on PubMed] ({art['url']})")
                st.markdown("---")
        else:
            st.warning("No articles found for the query.")
