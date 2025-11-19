from crewai.tools.base_tool import Tool, tool
import json
import re
import os 
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


#Loading local knowledge base from json
def load_kb():
    with open(os.path.join(BASE_DIR, "knowledge_base.json"), 'r', encoding="utf-8") as f:
        return json.load(f)
    
kb = load_kb()

## Tool 1: Local Product Research
def local_research(product_name: str) -> str:
    """Retrieve product data for `product_name` from the local knowledge base."""
    info = kb.get(product_name, {})
    if not info:
        return f"No offline date found for {product_name}"
    return json.dumps(info, indent=2)

local_research_tool = tool("local_research")(local_research)

# Tool 2: keyword_extractor

def keyword_extractor(text: str) -> str:
    """Extract important keywords (4+ letters) from `text` and return a comma-separated list."""
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    sorted_words = sorted(freq, key=freq.get, reverse=True)
    return ",".join(sorted_words[:15])


keyword_extractor_tool = tool("keyword_extractor")(keyword_extractor)

# Tool 3: Competitor Finder

def finder(product_name: str) -> str:
    """Return comma-separated competitor list for `product_name` from the KB."""
    item = kb.get(product_name, {})
    comp = item.get("competitors", [])
    return ",".join(comp) if comp else "No competitor data available."

competitor_tool = tool("competitor_finder")(finder)

    


