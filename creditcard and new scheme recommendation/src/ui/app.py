import streamlit as st
import json

from src.utils.logger import app_logger
from src.agents.coordinator import agent_graph
from src.explainability.query_traces import get_customer_decision_history, get_decision_trace

st.set_page_config(page_title="AI Credit Agent", page_icon="🏦", layout="wide")

def main():
    st.title("🏦 Neo4j-backed AI Credit Decision Agent")
    
    tab1, tab2 = st.tabs(["📝 Evaluate Eligibility", "🔍 Decision Audit Trace"])
    
    with tab1:
        st.header("New Credit Evaluation")
        with st.form("evaluation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                customer_id = st.text_input("Customer ID", value="CUST-")
            with col2:
                user_query = st.text_area("Customer Request", value="I would like to apply for a standard cashback credit card.")
                
            submit_button = st.form_submit_button("Evaluate")
            
        if submit_button:
            if customer_id and user_query:
                app_logger.info(f"UI Trigger: Starting evaluation for {customer_id}")
                
                with st.spinner("Agentic Workflow Interrogating Graph..."):
                    # Execute the LangGraph pipeline
                    try:
                        initial_state = {"customer_id": customer_id, "user_query": user_query, "errors": []}
                        result_state = agent_graph.invoke(initial_state)
                        
                        if result_state.get("errors"):
                            st.error(f"Evaluation failed: {', '.join(result_state['errors'])}")
                        else:
                            # Display Results
                            st.success(f"Final Decision: **{result_state['final_decision']}**")
                            st.subheader("LLM Rationale")
                            st.write(result_state['rationale'])
                            
                            with st.expander("Show Agent Graph State Details"):
                                st.json({
                                    "recommended_product_id": result_state.get('recommended_product_id'),
                                    "evaluated_rule_ids": result_state.get('evaluated_rule_ids'),
                                    "retrieved_policies_count": len(result_state.get('retrieved_policies', []))
                                })
                    except Exception as e:
                        app_logger.error(f"UI Error during evaluation: {e}")
                        st.error(f"An unexpected error occurred: {str(e)}")
            else:
                st.warning("Please provide both a Customer ID and a Request.")

    with tab2:
        st.header("Audit Customer Decisions")
        audit_customer_id = st.text_input("Enter Customer ID to Audit", value="CUST-")
        
        if st.button("Fetch History"):
            hist = get_customer_decision_history(audit_customer_id)
            if hist:
                st.dataframe(hist, use_container_width=True)
                
                st.markdown("### Deep Dive into a specific Decision Trace:")
                decision_to_audit = st.selectbox("Select a Decision ID", [h['decision_id'] for h in hist])
                
                if st.button("Load Full Graph Trace"):
                    trace = get_decision_trace(decision_to_audit)
                    if trace:
                        # Visualize trace details
                        st.json(trace)
            else:
                st.info("No historical decisions found for this customer.")

if __name__ == "__main__":
    main()
