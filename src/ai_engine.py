import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from models import ScrapeStrategy
from prompts import SYSTEM_PROMPT, ANALYSIS_PROMPT, SUMMARY_PROMPT

load_dotenv()

class AIEngine:
    def __init__(self):
        # Initialize Azure LLM
        # Ensure your .env has AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_DEPLOYMENT_NAME
        self.llm = AzureChatOpenAI(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            temperature=0
        )
        self.parser = PydanticOutputParser(pydantic_object=ScrapeStrategy)

    def analyze_page_structure(self, html_snippet: str) -> ScrapeStrategy:
        """Determines how to scrape the page using AI."""
        # Truncate HTML to fit context window (approx 30k chars is safe for GPT-4/3.5-16k)
        safe_html = html_snippet[:30000]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", ANALYSIS_PROMPT)
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            return chain.invoke({"html_content": safe_html})
        except Exception as e:
            print(f"⚠️ AI Analysis Error: {e}")
            # Robust Default Strategy if AI fails
            return ScrapeStrategy(
                page_type="single_page",
                item_container_selector="article, div[class*='product'], div[class*='card'], li",
                next_button_selector=None
            )

    def generate_summary(self, data_json: str) -> str:
        """Generates a summary of extracted data."""
        safe_data = str(data_json)[:8000] # Limit tokens
        prompt = ChatPromptTemplate.from_messages([("user", SUMMARY_PROMPT)])
        chain = prompt | self.llm | StrOutputParser()
        
        try:
            return chain.invoke({"data": safe_data})
        except Exception as e:
            return f"Summary unavailable. (Error: {e})"