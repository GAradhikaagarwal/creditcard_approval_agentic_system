import logging
from src.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

# List of Cypher constraints and indexes to initialize the schema
SCHEMA_STATEMENTS = [
    # Constraints for unique IDs
    "CREATE CONSTRAINT customer_id IF NOT EXISTS FOR (c:Customer) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT product_id IF NOT EXISTS FOR (p:Product) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT policy_clause_id IF NOT EXISTS FOR (pc:PolicyClause) REQUIRE pc.id IS UNIQUE",
    "CREATE CONSTRAINT decision_id IF NOT EXISTS FOR (d:Decision) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT account_id IF NOT EXISTS FOR (a:Account) REQUIRE a.id IS UNIQUE",
    
    # Indexes for fast text matching
    "CREATE INDEX product_name IF NOT EXISTS FOR (p:Product) ON (p.name)",
    "CREATE INDEX policy_type IF NOT EXISTS FOR (pc:PolicyClause) ON (pc.type)"
]

def initialize_schema():
    """
    Apply foundational schema constraints and indexes to the Neo4j database.
    This does not include vector indexes, which are handled separately in Phase 2.
    """
    logger.info("Initializing Neo4j schema constraints...")
    
    for statement in SCHEMA_STATEMENTS:
        try:
            neo4j_client.execute_query(statement)
            logger.info(f"Executed: {statement.split(' IF NOT EXISTS FOR')[0]}")
        except Exception as e:
            logger.error(f"Schema initialization failed for statement: {statement}")
            logger.error(str(e))
            raise
    
    logger.info("Graph schema created successfully!")

if __name__ == "__main__":
    # Basic logging config for when this file is run directly
    logging.basicConfig(level=logging.INFO)
    initialize_schema()
    neo4j_client.close()
