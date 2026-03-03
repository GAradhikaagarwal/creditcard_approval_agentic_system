import logging
from typing import List, Dict, Any

from src.db.neo4j_client import neo4j_client
from src.llm.embeddings import generate_embeddings

logger = logging.getLogger(__name__)

def perform_hybrid_search(
    user_query: str, 
    customer_id: str, 
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Executes a hybrid search: Combines vector similarity scoring against PolicyClauses
    with basic constraint filtering (e.g. minimum income checking) using Neo4j rules.
    
    Args:
        user_query (str): The natural language query from the customer.
        customer_id (str): The ID of the customer to apply rule filtering against.
        top_k (int): Number of top semantic matches to retrieve.
        
    Returns:
        List[Dict[str, Any]]: The prioritized, filtered policy matches and evidence.
    """
    logger.info(f"Starting hybrid search for Customer '{customer_id}' with query: '{user_query}'")
    
    try:
        # Step 1: Embed the user's query
        query_embedding = generate_embeddings([user_query])[0]
    except Exception as e:
        logger.error(f"Failed to generate query embedding: {e}")
        return []

    # Step 2: Execute Vector Search combined with filtering
    # We query the vector index for semantic similarity
    # AND we MATCH against the specific Customer's attributes to see if they pass basic rules.
    cypher_query = """
    // 1. Fetch the Customer data for hard-rule filtering
    MATCH (c:Customer {id: $customer_id})
    
    // 2. Perform Vector Search on 'policy_clause_embeddings' index
    CALL db.index.vector.queryNodes('policy_clause_embeddings', $top_k, $query_embedding)
    YIELD node AS policy_clause, score AS similarity_score
    
    // 3. Find the parent Product that owns this clause
    MATCH (product:Product)-[:HAS_CLAUSE]->(policy_clause)
    
    // 4. Hard Filter Application: Only return policies where the user meets base criteria
    // (This ensures we aren't recommending a premium card to someone without the income)
    WHERE c.monthly_income >= product.base_min_income 
      AND c.credit_score >= product.base_min_credit_score
      
    // 5. Structure the returning Evidence dictionary
    RETURN 
        product.id AS product_id,
        product.name AS product_name,
        policy_clause.id AS rule_id,
        policy_clause.text AS rule_text,
        similarity_score
    ORDER BY similarity_score DESC
    """
    
    parameters = {
        "customer_id": customer_id,
        "query_embedding": query_embedding,
        "top_k": top_k
    }

    try:
        results = neo4j_client.execute_query(cypher_query, parameters)
        logger.info(f"Hybrid search returned {len(results)} eligible policy clauses.")
        return results
    except Exception as e:
        logger.error(f"Hybrid search execution failed: {e}")
        return []

if __name__ == "__main__":
    # Test stub
    logging.basicConfig(level=logging.INFO)
    logger.info("Hybrid Search execution module loaded.")
