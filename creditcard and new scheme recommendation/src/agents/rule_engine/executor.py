import logging
from typing import Dict, Any, Optional
from src.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

def fetch_customer_data(customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches the customer's base profile from Neo4j.
    This acts as the 'Rule Engine' preprocessing step, gathering the empirical
    data needed before semantic retrieval and LLM decision-making.
    """
    logger.info(f"Rule Engine: Fetching data for Customer '{customer_id}'")
    
    query = """
    MATCH (c:Customer {id: $customer_id})
    OPTIONAL MATCH (c)-[:OWNS]->(a:Account)
    RETURN 
        c.id AS customer_id,
        c.name AS name,
        c.age AS age,
        c.monthly_income AS monthly_income,
        c.credit_score AS credit_score,
        collect({id: a.id, balance: a.balance, status: a.status}) AS accounts
    """
    
    try:
        results = neo4j_client.execute_query(query, {"customer_id": customer_id})
        if results:
            logger.info("Successfully fetched customer data.")
            return results[0]
        else:
            logger.warning(f"No customer found with ID: {customer_id}")
            return None
    except Exception as e:
        logger.error(f"Failed to fetch customer data: {e}")
        return None
