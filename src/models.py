from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ScrapeStrategy(BaseModel):
    """AI analysis result for page structure."""
    page_type: Literal["pagination", "infinite_scroll", "single_page"] = Field(
        ..., description="Navigation type: 'pagination' (numbers/next btn), 'infinite_scroll' (social media style), or 'single_page'."
    )
    item_container_selector: str = Field(
        ..., description="CSS selector for the repeatable item card (e.g., 'div.product-card', 'article.job-row')."
    )
    next_button_selector: Optional[str] = Field(
        None, description="CSS selector for the 'Next' or 'Load More' button."
    )

class ScrapedItem(BaseModel):
    """Universal data item."""
    title: str = "Unknown"
    price: Optional[str] = None
    link: Optional[str] = None
    snippet: Optional[str] = None