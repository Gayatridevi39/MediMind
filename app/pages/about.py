import streamlit as st
import os

st.set_page_config(
    page_title="MediMind-About",
    page_icon="app/assets/logo.png")


st.logo("app/assets/logo.png", size="large")
with st.sidebar:
    st.sidebar.title("🧭 Navigation")
    st.page_link("main.py", label="Home", icon="🏠")
    st.page_link("pages/about.py", label="About", icon="ℹ️")
    st.page_link("https://www.google.co.in/", label="Google", icon="🌎")
    
st.title("ℹ️ About MediMind")
st.markdown("---")

# logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logo.png'))

st.image("app/assets/logo.png", width=150)  # Optional: Add your logo here

st.markdown("""
### 🧠 What is MediMind?

**MediMind** is an AI-powered tool designed to **summarize and interpret complex medical reports** using advanced language models. It helps healthcare professionals, patients, and researchers quickly understand key insights from unstructured medical documents such as PDFs, text files, and CSVs.

Whether you're analyzing a radiology report, lab result, or discharge summary, MediMind simplifies medical jargon into **easy-to-understand language** — enabling faster decision-making and better patient engagement.

---

### 🚀 Key Features

- ✅ **Smart Text Extraction**: Extracts clean text from PDFs, .txt, .data, and .csv files.
- 📝 **AI Summarization**: Compresses long medical reports into concise summaries using HuggingFace transformers.
- 💬 **Interactive Q&A**: Ask questions directly about the report using **LangChain** + **Gemini** integration.
- ⚡ **Responsive UI**: Streamlit interface with a user-friendly sidebar, navigation, and hover effects.
- 🔐 **Secure**: API keys managed via `.env` for safe and modular development.

---

### 🧑‍💻 Technologies Used

- **Python 3.10**
- **Streamlit** - Web interface
- **LangChain** - LLM orchestration
- **Gemini (Google Generative AI)** - LLM for answering and interpreting medical queries
- **Hugging Face Transformers** - For medical text summarization
- **PyMuPDF (fitz)** - For PDF parsing
- **dotenv** - API key management

---

### 🌍 Why This Project Matters

The healthcare industry is overwhelmed with data — but much of it is locked inside complex, unstructured reports. MediMind helps unlock this data by:

- Reducing **manual interpretation effort**
- Improving **patient comprehension**
- Accelerating **clinical workflows**

This project showcases how modern **AI and NLP** can be practically applied to make a **real-world impact** in the healthcare space.

---

### 👥 Meet the Team

This project is developed as part of an AI Engineering internship by a dedicated student :

- 👩‍💻 **Gayatri Devi Kajuluri** *( AI Developer)*


We are passionate about building AI solutions that **solve meaningful problems** and excited to contribute to the future of medical technology.

---

### 📫 Contact

Have suggestions or ideas to improve MediMind? Reach out to us or contribute to the future of healthcare AI!

""")
