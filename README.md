# 🩺 Medical Report Summarizer & Interpreter

An AI-powered Streamlit application that **extracts, summarizes, and interprets** medical reports using **LangChain** and **Gemini (Google Generative AI)**. Designed to assist doctors, healthcare analysts, and researchers in understanding patient records efficiently.

---

## 🚀 Features

- 📄 **Upload Medical Reports** (`.pdf`, `.csv`, `.txt`, `.data`)
- 🔍 **Automatic Text Extraction** using PyMuPDF & Pandas
- 🧠 **LLM-Powered Summarization** of full medical reports
- ❓ **Ask Questions** about the report and get intelligent answers
- 💬 **Google Gemini + LangChain Integration** for contextual responses
- ⬇️ **Downloadable Summary** feature (optional)
- 🧪 **Sample Report Support** for demo/testing

---

## 💡 Use Case

Doctors and medical professionals often review lengthy and complex patient records. This tool:

- Summarizes medical reports instantly
- Answers doctor’s queries contextually
- Saves time and reduces manual workload

---

## 🛠️ Tech Stack

| Tech             | Purpose                                |
|------------------|----------------------------------------|
| `Streamlit`      | Web interface                          |
| `LangChain`      | Chain management for LLM interactions  |
| `Gemini API`     | Google Generative AI (LLM backend)     |
| `PyMuPDF (fitz)` | Extract text from PDF medical reports  |
| `pandas`         | Handle CSV and data files              |
| `transformers`   | Traditional summarization pipeline     |
| `.env`           | Store Gemini API Key securely          |

---

## 📸 UI Preview 

![App Screenshot](assets/app.png)

---

## 🧑‍💻 How to Run the App Locally

1. **Clone the repository**

`bash`
```
git clone https://github.com/yourusername/medical-report-summarizer.git
cd medical-report-summarizer
```


## 🔐 Environment Variables

| Variable     | Description                       |
| ------------ | --------------------------------- |
| `GEMINI_KEY` | Your Google Generative AI API Key |



## 🤝 Authors

- Gayatri Devi Kajuluri

- Shiva Teja Medoju

- Mattaparthi Tejaswini

- Meesala Shivani

---

## 📬 Contact

If you have any questions or suggestions, feel free to reach out at [kajulurigayatridevi@gmail.com].

## ⭐ Future Enhancements

- 🏥 Integration with patient health databases (EHR/EMR)
- 📊 Visual analytics of patient health indicators
- 🗣️ Voice-based report Q&A using speech-to-text
- 🧾 Named Entity Recognition (NER) for extracting medical entities


## 📢 Disclaimer

This tool is for educational and research purposes only and is not approved for clinical diagnosis. Use responsibly.
