import streamlit as st
from firecrawl import Firecrawl
from services.logger_service import get_logger

logger = get_logger(__name__)

def search_with_firecrawl(query: str):
    """
    Searches for real estate data using the Firecrawl API.

    Args:
        query: The search query, including the deceased's name and other relevant info.

    Returns:
        A list of search results, or an error message if the search fails.
    """
    logger.info(f"Performing Firecrawl search for: {query}")
    try:
        api_key = st.secrets["FIRECRAWL_API_KEY"]
        if not api_key or api_key == "fc-YOUR_API_KEY":
            logger.error("Firecrawl API key not configured.")
            return "Firecrawl API key not configured. Please add it to your secrets."
    except (FileNotFoundError, KeyError):
        logger.error("Firecrawl API key not found in secrets.toml.")
        return "Firecrawl API key not found. Please create a .streamlit/secrets.toml file with your key."

    client = Firecrawl(api_key=api_key)

    try:
        response = client.search(query)
        logger.info(f"Firecrawl search successful for: {query}")
        return response.dict()
    except Exception as e:
        logger.error(f"Firecrawl search failed for '{query}': {e}", exc_info=True)
        return f"An error occurred during the Firecrawl search: {e}"