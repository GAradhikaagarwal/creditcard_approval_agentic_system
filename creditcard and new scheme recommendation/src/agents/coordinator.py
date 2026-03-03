from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    """
    The shared state dictionary that is passed between LangGraph nodes.
    This acts as the "memory" for a single execution run of the agent graph.
    """
    
    # Inputs
    customer_id: str
    user_query: str
    
    # Intermediary State (Populated by Nodes)
    customer_data: Optional[Dict[str, Any]]
    retrieved_policies: List[Dict[str, Any]]
    
    # Outputs (Populated by the final Decision Node)
    final_decision: Optional[str]
    rationale: Optional[str]
    recommended_product_id: Optional[str]
    evaluated_rule_ids: List[str]
    
    # Error Handling / Control Flow
    errors: List[str]
