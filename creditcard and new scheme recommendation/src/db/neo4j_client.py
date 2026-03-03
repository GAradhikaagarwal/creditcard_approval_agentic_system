import os
import logging
from neo4j import GraphDatabase, Driver
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
            logger.info("Connected to Neo4j successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        if hasattr(self, "driver") and self.driver:
            self.driver.close()
            logger.info("Neo4j driver closed.")

    def execute_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query and return the results."""
        parameters = parameters or {}
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            logger.error(f"Query: {query}")
            raise

neo4j_client = Neo4jClient()
