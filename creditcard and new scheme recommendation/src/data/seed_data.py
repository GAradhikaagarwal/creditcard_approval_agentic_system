import random
import logging
import uuid
from typing import List, Dict

from src.db.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

# Sample static data for generation
FIRST_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Hank"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson"]

def generate_customers(count: int) -> List[Dict]:
    customers = []
    for _ in range(count):
        customers.append({
            "id": f"CUST-{uuid.uuid4().hex[:8]}",
            "name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            "age": random.randint(21, 65),
            "monthly_income": round(random.uniform(2000, 15000), 2),
            "credit_score": random.randint(500, 850)
        })
    return customers

def get_base_products() -> List[Dict]:
    return [
        {
            "id": "PROD-CC-001",
            "name": "Standard Cashback Credit Card",
            "base_min_income": 3000,
            "base_min_credit_score": 600,
            "product_type": "CREDIT_CARD"
        },
        {
            "id": "PROD-CC-002",
            "name": "Premium Travel Rewards Card",
            "base_min_income": 6000,
            "base_min_credit_score": 720,
            "product_type": "CREDIT_CARD"
        },
        {
            "id": "PROD-LOAN-001",
            "name": "Personal Starter Loan",
            "base_min_income": 2000,
            "base_min_credit_score": 580,
            "product_type": "PERSONAL_LOAN"
        }
    ]

def ingest_data(num_customers=50):
    logger.info("Starting synthetic data ingestion...")
    
    # 1. Clear existing generic data (Careful in production!)
    logger.warning("Clearing existing Customer, Product, and Account nodes for a fresh slate.")
    neo4j_client.execute_query("MATCH (n:Customer) DETACH DELETE n")
    neo4j_client.execute_query("MATCH (n:Product) DETACH DELETE n")
    neo4j_client.execute_query("MATCH (n:Account) DETACH DELETE n")

    # 2. Ingest Products
    products = get_base_products()
    for p in products:
        query = """
        CREATE (pr:Product {
            id: $id, 
            name: $name, 
            base_min_income: $base_min_income, 
            base_min_credit_score: $base_min_credit_score,
            product_type: $product_type
        })
        """
        neo4j_client.execute_query(query, p)
    logger.info(f"Ingested {len(products)} products.")

    # 3. Ingest Customers and Accounts using UNWIND for batching efficiency
    customers = generate_customers(num_customers)
    
    batch_customer_query = """
    UNWIND $customers AS cust
    CREATE (c:Customer {
        id: cust.id,
        name: cust.name,
        age: cust.age,
        monthly_income: cust.monthly_income,
        credit_score: cust.credit_score
    })
    // Optionally create an Account connected to the Customer
    CREATE (a:Account {
        id: 'ACC-' + cust.id,
        status: 'ACTIVE',
        balance: round(rand() * 5000 * 100) / 100
    })
    CREATE (c)-[:OWNS]->(a)
    """
    neo4j_client.execute_query(batch_customer_query, {"customers": customers})
    logger.info(f"Ingested {len(customers)} customers and linked accounts.")
    logger.info("Data seeding complete.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    ingest_data(num_customers=50) # Use smaller set for POC testing
    neo4j_client.close()
