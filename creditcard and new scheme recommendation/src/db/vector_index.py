import logging
from src.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

def create_vector_index():
    """
    Creates the vector index on the PolicyClause nodes in Neo4j for semantic search.
    Requires Neo4j 5+.
    """
    logger.info("Initializing Vector Index for PolicyClauses...")
    
    # Example using Neo4j 5+ vector index syntax
    # We index the 'embedding' property of 'PolicyClause' nodes.
    # The dimension depends on the model used (e.g., 768 or 1536). Together AI's M2-BERT is 768.
    
    check_index_query = "SHOW INDEXES YIELD name, type WHERE type = 'VECTOR' AND name = 'policy_clause_embeddings'"
    create_index_query = """
    CREATE VECTOR INDEX policy_clause_embeddings IF NOT EXISTS
    FOR (p:PolicyClause)
    ON (p.embedding)
    OPTIONS {indexConfig: {
      `vector.dimensions`: 768,
      `vector.similarity_function`: 'cosine'
    }}
    """
    
    try:
        existing_indexes = neo4j_client.execute_query(check_index_query)
        if hasattr(existing_indexes, '__len__') and len(existing_indexes) > 0:
            logger.info("Vector index 'policy_clause_embeddings' already exists.")
        else:
            neo4j_client.execute_query(create_index_query)
            logger.info("Vector index 'policy_clause_embeddings' created successfully.")
            
        # Optional: wait for index to populate
        neo4j_client.execute_query("CALL db.awaitIndex('policy_clause_embeddings')")
        
    except Exception as e:
        logger.error(f"Failed to create vector index: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    create_vector_index()
    neo4j_client.close()
