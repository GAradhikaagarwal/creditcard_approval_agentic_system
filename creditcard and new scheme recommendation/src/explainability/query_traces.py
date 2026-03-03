import logging
from typing import List, Dict, Any
from src.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

def get_decision_trace(decision_id: str) -> Dict[str, Any]:
    """
    Retrieves the full explainability trace for a given Decision node ID.
    This fetches the Customer context, the Product evaluated, and the specific
    PolicyClauses the LLM used to form its rationale.
    """
    logger.info(f"Fetching trace for Decision '{decision_id}'")
    
    query = """
    MATCH (d:Decision {id: $decision_id})
    OPTIONAL MATCH (d)-[:MADE_FOR]->(c:Customer)
    OPTIONAL MATCH (d)-[:EVALUATED_AGAINST]->(p:Product)
    OPTIONAL MATCH (d)-[:BASED_ON]->(pc:PolicyClause)
    
    RETURN 
        d.id AS decision_id,
        d.outcome AS outcome,
        d.rationale AS rationale,
        d.timestamp AS timestamp,
        { id: c.id, name: c.name } AS customer,
        { id: p.id, name: p.name } AS product,
        collect({ id: pc.id, text: pc.text }) AS rule_evidence
    """
    
    try:
        results = neo4j_client.execute_query(query, {"decision_id": decision_id})
        if results:
            return results[0]
        else:
            logger.warning(f"No Decision trace found for ID: {decision_id}")
            return {}
    except Exception as e:
        logger.error(f"Failed to fetch decision trace: {e}")
        return {}
        
def get_customer_decision_history(customer_id: str) -> List[Dict[str, Any]]:
    """
    Fetches all historical decisions made for a specific Customer.
    """
    query = """
    MATCH (d:Decision)-[:MADE_FOR]->(c:Customer {id: $customer_id})
    OPTIONAL MATCH (d)-[:EVALUATED_AGAINST]->(p:Product)
    RETURN 
        d.id AS decision_id,
        d.outcome AS outcome,
        d.timestamp AS timestamp,
        p.name AS product_name
    ORDER BY d.timestamp DESC
    """
    
    try:
        return neo4j_client.execute_query(query, {"customer_id": customer_id})
    except Exception as e:
        logger.error(f"Failed to fetch customer decision history: {e}")
        return []
