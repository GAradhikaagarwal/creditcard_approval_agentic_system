import os
import requests
import logging
from typing import List

logger = logging.getLogger(__name__)

def generate_embeddings(texts: List[str], model: str = "togethercomputer/m2-bert-80M-8k-retrieval") -> List[List[float]]:
    """
    Generate embeddings for a list of strings using the Together AI API.
    
    Args:
        texts (List[str]): A list of text documents/strings to embed.
        model (str): The specific model name on Together AI. Dimensions must match Neo4j index.
        
    Returns:
        List[List[float]]: A list of embedding float arrays.
    """
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.error("TOGETHER_API_KEY is not set.")
        raise ValueError("TOGETHER_API_KEY environment variable is required.")

    url = "https://api.together.xyz/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": texts
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        
        data = response.json()
        
        # The API returns a list of data objects, each containing an 'embedding' array
        # We need to sort them by index to ensure they match the input list order
        sorted_data = sorted(data.get("data", []), key=lambda x: x.get("index", 0))
        
        embeddings = [item["embedding"] for item in sorted_data]
        return embeddings
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to generate embeddings via Together API: {e}")
        if e.response is not None:
             logger.error(f"Response Content: {e.response.text}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
         # Small self-test
         sample_texts = ["Credit card policy for premium users", "Loan requirement details"]
         res = generate_embeddings(sample_texts)
         logger.info(f"Successfully generated {len(res)} embeddings. Dimensions: {len(res[0])}")
    except Exception as e:
         logger.warning(f"Self-test failed (likely missing API key): {e}")

