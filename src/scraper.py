import asyncio
import sys
import re
from typing import List
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
from models import ScrapeStrategy, ScrapedItem

# Fix for Windows Asyncio loop
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

class SmartScraper:
    def __init__(self, headless=False):
        self.headless = headless
        self.user_data_dir = "./browser_session" # Keeps you logged in

    async def get_clean_html(self, page: Page) -> str:
        """Removes noise (scripts, styles) to give AI a clear view."""
        await page.wait_for_load_state("domcontentloaded")
        content = await page.content()
        soup = BeautifulSoup(content, "lxml")
        
        # Remove junk tags
        for tag in soup(["script", "style", "svg", "noscript", "iframe", "footer", "nav"]):
            tag.decompose()
            
        return str(soup.find("body") or soup)

    async def extract_smart_data(self, page: Page, selector: str) -> List[ScrapedItem]:
        """
        Universal Extractor:
        1. Tries the AI selector.
        2. If AI selector fails, tries generic 'card' selectors.
        3. Inside the card, intelligently hunts for Title, Price, and Link.
        """
        items_data = []
        
        # 1. Gather Elements
        try:
            await page.wait_for_selector(selector, timeout=3000)
        except:
            print(f"⚠️ AI Selector '{selector}' not found. Trying generic fallback.")
            # Fallback for ANY website (cards, articles, list items)
            selector = "article, div[class*='product'], div[class*='card'], div[class*='item'], li"

        # Get HTML of all potential items
        elements_html = await page.evaluate(f"""(sel) => {{
            return Array.from(document.querySelectorAll(sel)).map(e => e.outerHTML);
        }}""", selector)

        # 2. Parse Each Item
        for html in elements_html:
            soup = BeautifulSoup(html, "lxml")
            text_content = soup.get_text(" ", strip=True)
            
            # Skip empty trash elements
            if len(text_content) < 5: 
                continue

            # --- SMART HEURISTICS ---
            
            # A. Title Extraction (Priority: H-tags -> Link Text -> Bold text)
            title = "Unknown"
            header = soup.find(['h1', 'h2', 'h3', 'h4', 'strong'])
            if header:
                title = header.get_text(strip=True)
            else:
                link_tag = soup.find("a")
                if link_tag and len(link_tag.get_text(strip=True)) > 0:
                    title = link_tag.get_text(strip=True)
            
            # B. Price Extraction (Universal Regex for currencies)
            # Matches: $10, £50.00, 500 USD, €20
            price_match = re.search(r'([$£€¥₹]\s?[\d,.]+|[\d,.]+\s?(USD|EUR|GBP|INR))', text_content)
            price = price_match.group(0) if price_match else None

            # C. Link Extraction
            link_el = soup.find("a")
            link = link_el['href'] if link_el else None
            
            # Only add if we found something useful
            if title != "Unknown" or price:
                items_data.append(ScrapedItem(
                    title=title,
                    price=price,
                    link=link,
                    snippet=text_content[:150]
                ))

        return items_data

    async def run_scraper(self, url: str, ai_engine, max_pages=1):
        """Main generator loop."""
        async with async_playwright() as p:
            # Persistent context for login sessions
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 800}
            )
            
            page = context.pages[0] if context.pages else await context.new_page()
            scraped_data = []

            try:
                yield "status", f"Navigating to {url}..."
                await page.goto(url, wait_until="domcontentloaded")
                await asyncio.sleep(2) # Wait for JS render

                # --- STEP 1: AI ANALYSIS ---
                yield "status", "🧠 AI Analyzing Page Structure..."
                clean_html = await self.get_clean_html(page)
                strategy = ai_engine.analyze_page_structure(clean_html)
                
                yield "status", f"Strategy: {strategy.page_type.upper()} | Target: {strategy.item_container_selector}"

                # --- STEP 2: SCRAPING LOOP ---
                current_page = 1
                while current_page <= max_pages:
                    yield "progress", (current_page / max_pages)

                    # Extract
                    new_items = await self.extract_smart_data(page, strategy.item_container_selector)
                    
                    # Deduplicate (by link)
                    existing_links = {x.link for x in scraped_data}
                    for item in new_items:
                        if item.link not in existing_links:
                            scraped_data.append(item)
                            existing_links.add(item.link)

                    yield "data", new_items

                    # Handle Navigation
                    if strategy.page_type == "infinite_scroll":
                        yield "status", "Scrolling down..."
                        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        await asyncio.sleep(2)
                        current_page += 0.5 # Count scrolls differently
                    
                    elif strategy.page_type == "pagination" and strategy.next_button_selector:
                        try:
                            # Check if button exists
                            if await page.query_selector(strategy.next_button_selector):
                                yield "status", "Clicking Next Page..."
                                await page.click(strategy.next_button_selector)
                                await page.wait_for_load_state("domcontentloaded")
                                await asyncio.sleep(2)
                                current_page += 1
                            else:
                                yield "status", "No more pages found."
                                break
                        except:
                            break # Click failed
                    else:
                        break # Single page

                yield "complete", scraped_data

            except Exception as e:
                yield "status", f"Error: {str(e)}"
            finally:
                await context.close()