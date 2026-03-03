import os
import logging
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from groq import Groq
import instructor

logger = logging.getLogger(__name__)

# Define the structured output schema we expect from the LLM
class DecisionOutput(BaseModel):
    decision: str = Field(description="The final decision: 'APPROVE', 'REJECT', or 'REFER'.")
    rationale: str = Field(description="A detailed explanation of why this decision was reached based on the rules and customer data.")
    product_id: Optional[str] = Field(description="The ID of the recommended product, if applicable.")
    rule_ids_evaluated: list[str] = Field(description="A list of the policy clause IDs that were evaluated to make this decision.")

def evaluate_decision_with_llm(
    customer_data: Dict[str, Any], 
    retrieved_policies: list[Dict[str, Any]], 
    query: str
) -> DecisionOutput:
    """
    Uses Groq (via Instructor for structured JSON output) to evaluate a customer's
    eligibility based on retrieved Neo4j policy clauses.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        logger.error("GROQ_API_KEY is not set.")
        raise ValueError("GROQ_API_KEY environment variable is required.")

    # Apply the Instructor patch to the Groq client to force Structured Outputs
    client = instructor.from_groq(Groq(api_key=api_key))
    
    system_prompt = """
    You are a strict, objective financial AI agent. Your job is to evaluate if a customer 
    is eligible for a specific financial product based ONLY on the provided policy rules.
    
    You must output a structured JSON response containing:
    1. decision: APPROVE, REJECT, or REFER.
    2. rationale: Why you made the decision.
    3. product_id: The ID of the product being considered.
    4. rule_ids_evaluated: The specific rule IDs you used to decide.
    """
    
    user_prompt = f"""
    Customer Data: {customer_data}
    User Request: {query}
    Retrieved Policies / Rules: {retrieved_policies}
    
    Evaluate the customer against the rules and provide your final decision.
    """

    try:
        # LLM Call requesting structured output based on the DecisionOutput Pydantic model
        decision: DecisionOutput = client.chat.completions.create(
            model="llama3-70b-8192", # Fast and capable open-source model via Groq
            response_model=DecisionOutput,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0 # We want deterministic logic, not creativity
        )
        logger.info(f"LLM Decision generated successfully: {decision.decision}")
        return decision
        
    except Exception as e:
        logger.error(f"Failed to generate LLM decision: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger.info("LLM Decision Client loaded.")
