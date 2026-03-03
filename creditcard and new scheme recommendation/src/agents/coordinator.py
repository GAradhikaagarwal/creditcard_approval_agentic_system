import logging
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from src.agents.rule_engine.executor import fetch_customer_data
from src.agents.retrieval.executor import perform_hybrid_search
from src.agents.decision.executor import make_decision

logger = logging.getLogger(__name__)

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

# --- Nodes ---

def rule_engine_node(state: AgentState) -> AgentState:
    logger.info("--- NODE: Rule Engine (Customer Data Fetch) ---")
    customer_id = state.get("customer_id")
    if not customer_id:
        state["errors"].append("Missing customer_id.")
        return state
        
    data = fetch_customer_data(customer_id)
    if data:
        state["customer_data"] = data
    else:
        state["errors"].append(f"Customer {customer_id} not found in graph.")
    return state

def retrieval_node(state: AgentState) -> AgentState:
    logger.info("--- NODE: Retrieval (Hybrid Search) ---")
    if state.get("errors"):
        logger.warning("Skipping retrieval due to prior errors.")
        return state
        
    policies = perform_hybrid_search(
        user_query=state["user_query"],
        customer_id=state["customer_id"],
        top_k=3
    )
    state["retrieved_policies"] = policies
    return state

from src.explainability.decision_tracer import record_decision

def decision_node(state: AgentState) -> AgentState:
    logger.info("--- NODE: Decision (LLM Evaluation) ---")
    if state.get("errors"):
        logger.warning("Skipping Decision node due to prior errors.")
        return state
        
    try:
        decision_obj = make_decision(
            customer_data=state.get("customer_data", {}),
            retrieved_policies=state.get("retrieved_policies", []),
            user_query=state["user_query"]
        )
        
        state["final_decision"] = decision_obj.decision
        state["rationale"] = decision_obj.rationale
        state["recommended_product_id"] = decision_obj.product_id
        state["evaluated_rule_ids"] = decision_obj.rule_ids_evaluated
        
        # Persist the decision trace directly to Neo4j
        if decision_obj.product_id:
            record_decision(
                customer_id=state["customer_id"],
                product_id=decision_obj.product_id,
                decision_outcome=decision_obj.decision,
                rationale=decision_obj.rationale,
                evaluated_rule_ids=decision_obj.rule_ids_evaluated
            )
            
    except Exception as e:
        logger.error(f"Decision node failed: {e}")
        state["errors"].append(f"LLM Decision failed: {str(e)}")
        
    return state

# --- Routing Logic ---

def route_after_rule_engine(state: AgentState):
    if state.get("errors"):
        return END
    return "retrieval_node"

def route_after_retrieval(state: AgentState):
    if state.get("errors"):
        return END
    return "decision_node"

# --- Graph Compilation ---

def build_graph():
    """Constructs the LangGraph DAG for the credit eligibility agent."""
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("rule_engine_node", rule_engine_node)
    workflow.add_node("retrieval_node", retrieval_node)
    workflow.add_node("decision_node", decision_node)
    
    # Define Edges
    workflow.add_edge(START, "rule_engine_node")
    workflow.add_conditional_edges("rule_engine_node", route_after_rule_engine)
    workflow.add_conditional_edges("retrieval_node", route_after_retrieval)
    workflow.add_edge("decision_node", END)
    
    # Compile
    app = workflow.compile()
    logger.info("LangGraph Agent Execution Graph compiled successfully.")
    return app

# The instantiated compiled graph
agent_graph = build_graph()
