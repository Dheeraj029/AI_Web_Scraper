# AI_Web_Scraper# 

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)
![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-0078D4?style=for-the-badge&logo=microsoftazure)
![Playwright](https://img.shields.io/badge/Playwright-45BA4B?style=for-the-badge&logo=google-chrome)

An enterprise-grade autonomous scraping agent that uses **Azure OpenAI (GPT-4)** to analyze website structures, detect pagination logic, and extract structured data automatically. Built with **Streamlit**, **Playwright**, and **LangChain**.

---

## 🚀 Key Features

- 🧠 **AI Structure Analysis**: Detects Pagination, Infinite Scroll, or Single Page.
- 🤖 **Smart Selector Detection** using LLM reasoning.
- 🕷️ **Browser Automation** with Playwright persistent login.
- 🛡️ Anti-bot safer browser setup.
- 📊 AI-generated data summaries.
- 📥 CSV export.
- ⚡ Windows async compatibility fix.

---

## 🧠 How It Works

1. HTML Cleaning removes scripts, styles, ads.
2. Azure OpenAI analyzes page structure.
3. AI decides navigation logic.
4. Scraper follows AI strategy.
5. Data is structured via Pydantic.

---

## 🛠️ Tech Stack

| Component | Technology |
|----------|------------|
| Frontend | Streamlit |
| AI | LangChain + Azure OpenAI |
| Browser | Playwright |
| Parsing | BeautifulSoup + Pydantic |

---

## ⚙️ Installation

### 1️⃣ Clone Repo
```bash
git clone https://github.com/yourusername/ai-web-scraper.git
cd ai-web-scraper
```

### 2️⃣ Virtual Environment
```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Install Playwright Browsers
```bash
python -m playwright install
```

---

## 🔑 .env Configuration

```ini
AZURE_OPENAI_API_KEY=your_actual_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_DEPLOYMENT_NAME=your_deployment_name
```

---

## 🚀 Run the App

```bash
streamlit run main.py
```



