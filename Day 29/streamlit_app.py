import streamlit as st
from app import IncidentRAG

st.set_page_config(page_title="AI Incident Finder", page_icon="🛡️")
st.title("🛡️ AI Incident Finder")
st.caption("Offline RAG system for real-world AI ethics & safety incidents")

@st.cache_resource
def get_rag():
    return IncidentRAG()

rag = get_rag()
query = st.text_input("Ask a question about an AI ethics incident:", placeholder="e.g. How did AI bias hiring resumes?")

if st.button("Search Incidents") and query:
    result = rag.query(query)
    st.metric("Retrieval Confidence", f"{result['confidence']:.2%}")
    if result["guardrail_triggered"]:
        st.warning(result["answer"])
    else:
        st.success("Relevant Incident Found:")
        st.write(result["answer"])
        st.subheader("Cited Sources")
        for src in result["sources"]:
            st.markdown(f"- **{src['title']}** ({src['year']}) · *{src['category']}* (Score: {src['similarity']:.2%})")
