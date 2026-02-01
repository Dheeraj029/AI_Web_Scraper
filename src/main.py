import streamlit as st
import asyncio
import pandas as pd
import nest_asyncio
import os
from scraper import SmartScraper
from ai_engine import AIEngine
from dotenv import load_dotenv

nest_asyncio.apply()
load_dotenv()

st.set_page_config(page_title="AI Web Scraper", page_icon="🕸️", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    div[data-testid="stMetric"] { background-color: #262730; border-radius: 10px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return AIEngine()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Settings")
    headless = st.toggle("Headless Mode", False, help="Hide browser window")
    max_pages = st.slider("Max Pages / Scrolls", 1, 10, 2)
    st.divider()
    if st.button("🧹 Clear Cache"):
        import shutil
        try: shutil.rmtree("./browser_session") 
        except: pass
        st.success("Session Cleared")

# --- Main ---
st.title("🕸️ AI Web Scraper")
st.caption("Playwright • Azure OpenAI • Auto-Structure Detection")

url = st.text_input("Target URL", "https://books.toscrape.com/")
start = st.button("🚀 Launch Scraper", type="primary")

if "results" not in st.session_state:
    st.session_state.results = pd.DataFrame()

async def run_workflow():
    engine = get_engine()
    scraper = SmartScraper(headless=headless)
    
    status = st.status("Initializing...", expanded=True)
    pbar = st.progress(0)
    data_view = st.empty()
    all_data = []

    async for kind, payload in scraper.run_scraper(url, engine, max_pages):
        if kind == "status":
            status.write(f"🔹 {payload}")
        elif kind == "progress":
            pbar.progress(min(payload, 1.0))
        elif kind == "data":
            # Real-time update
            batch = [i.model_dump() for i in payload]
            all_data.extend(batch)
            df = pd.DataFrame(all_data)
            data_view.dataframe(df.tail(5), use_container_width=True)
        elif kind == "complete":
            status.update(label="Done!", state="complete", expanded=False)
            return pd.DataFrame([i.model_dump() for i in payload])
            
    return pd.DataFrame()

if start:
    if not os.getenv("AZURE_OPENAI_API_KEY"):
        st.error("❌ Missing Azure Keys in .env file")
    else:
        with st.spinner("Agent working..."):
            st.session_state.results = asyncio.run(run_workflow())

# --- Output Section ---
if not st.session_state.results.empty:
    st.divider()
    df = st.session_state.results
    
    tab1, tab2, tab3 = st.tabs(["📄 Data", "📊 Analytics", "🧠 AI Summary"])
    
    with tab1:
        st.dataframe(df, use_container_width=True, height=500)
        st.download_button("📥 Download CSV", df.to_csv(index=False), "scraped_data.csv")
        
    with tab2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Items Found", len(df))
        c2.metric("Unique Links", df['link'].nunique())
        c3.metric("Prices Found", df['price'].notna().sum())
        
    with tab3:
        if st.button("Generate Summary"):
            engine = get_engine()
            with st.spinner("Analyzing data..."):
                # Pass a sample to save tokens
                summary = engine.generate_summary(df.head(15).to_json())
                st.markdown(summary)