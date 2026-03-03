import logging
from typing import Dict, Any
from src.llm.llm_client import evaluate_decision_with_llm

logger = logging.getLogger(__name__)

def make_decision(customer_data: Dict[str, Any], retrieved_policies: list[Dict[str, Any]], user_query: str):
    """
    Executes the Decision Node.
    Passes the context and policies to the Groq LLM via Instructor to get a structured JSON outcome.
    """
    logger.info("Decision Node: Evaluating aggregated data via LLM...")
    
    if not customer_data:
        logger.error("Decision Node failed: No customer data provided.")
        raise ValueError("Cannot make decision without customer data.")
        
    if not retrieved_policies:
        logger.warning("Decision Node: No eligible policies retrieved. Likely a REJECT.")
        # Note: We can either short-circuit here to a REJECT or let the LLM handle it.
        # Letting the LLM generate a polite rationale is generally better UX.
        
    try:
        decision_output = evaluate_decision_with_llm(
            customer_data=customer_data,
            retrieved_policies=retrieved_policies,
            query=user_query
        )
        logger.info(f"Decision Node: LLM returned final outcome '{decision_output.decision}'.")
        return decision_output
    except Exception as e:
        logger.error(f"Decision Node execution failed: {e}")
        raise
