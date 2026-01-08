import streamlit as st
import requests
import json

# API configuration
API_BASE_URL = "http://localhost:8000/api/v1"

st.set_page_config(page_title="Vector Database Chatbot", layout="wide")

st.title("🧠 Vector Database Chatbot")
st.markdown("Chat with your documents using Ollama and ChromaDB")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "documents" not in st.session_state:
    st.session_state.documents = []

# Sidebar for database operations (MUST be at the top, before any other elements)
with st.sidebar:
    st.header("Database Operations")
    
    if st.button("🔄 Seed Database with Sample Docs"):
        with st.spinner("Seeding database..."):
            try:
                response = requests.post(f"{API_BASE_URL}/seed/")
                if response.status_code == 200:
                    st.success("Database seeded successfully!")
                else:
                    st.error(f"Failed to seed database: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Make sure the backend server is running on http://localhost:8000")
    
    if st.button("📊 View Database Stats"):
        with st.spinner("Loading stats..."):
            try:
                response = requests.get(f"{API_BASE_URL}/stats/")
                if response.status_code == 200:
                    data = response.json()
                    st.info(f"Total Documents: {data['total_documents']}")
                    if data.get('document_ids'):
                        with st.expander("View Document IDs"):
                            for doc_id in data['document_ids']:
                                st.code(doc_id)
                else:
                    st.error(f"Failed to load stats: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    st.header("Document Management")
    
    # Create new document
    with st.expander("📝 Add New Document"):
        doc_content = st.text_area("Document Content", height=150, 
                                 placeholder="Enter document text here...")
        doc_metadata = st.text_input("Metadata (JSON)", 
                                    value='{"source": "user", "topic": "general"}',
                                    help="Enter metadata as JSON object")
        
        if st.button("Save Document", key="save_doc_btn"):
            if doc_content:
                try:
                    metadata = json.loads(doc_metadata) if doc_metadata else {}
                    payload = {"content": doc_content, "metadata": metadata}
                    
                    with st.spinner("Saving document..."):
                        response = requests.post(f"{API_BASE_URL}/documents/", json=payload)
                    
                    if response.status_code == 200:
                        st.success("Document saved successfully!")
                        st.rerun()
                    else:
                        st.error(f"Failed to save document: {response.text}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON in metadata. Use format: {\"key\": \"value\"}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter document content")

# Main layout - Use tabs instead of columns for better organization
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Search", "📚 Documents"])

with tab1:
    # Chat interface - This needs to be at the top level, not inside columns
    st.subheader("Chat with Documents")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message.get("sources"):
                with st.expander("📚 View Sources"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Source {i+1}**")
                        st.markdown(f"**ID:** `{source['id'][:20]}...`")
                        st.markdown(f"**Content:** {source['content'][:300]}...")
                        if source.get('distance'):
                            st.markdown(f"**Relevance Score:** {(1 - source['distance']):.3f}")
                        st.divider()
    
    # Chat input - MUST be at the end of the tab, at top level
    # Don't place this inside any container, column, or expander

with tab2:
    st.subheader("Direct Vector Search")
    
    query = st.text_input("Search query", placeholder="Enter your search query...")
    top_k = st.slider("Number of results", 1, 10, 3, key="search_top_k")
    
    if st.button("Search Documents", key="search_btn"):
        if query:
            with st.spinner("Searching..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/query/",
                        json={"query": query, "top_k": top_k}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        st.success(f"Found {data['total_matches']} results")
                        
                        for i, result in enumerate(data["results"]):
                            with st.expander(f"Result {i+1}: {result['id'][:20]}...", expanded=i==0):
                                st.write(result["content"])
                                st.caption(f"**Metadata:** {result['metadata']}")
                                if result.get('distance'):
                                    st.caption(f"**Distance:** {result['distance']:.4f}")
                    else:
                        st.error(f"Search failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter a search query")

with tab3:
    st.subheader("All Documents in Database")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Load Documents", key="load_docs_btn"):
            st.session_state.documents = []  # Clear cache
            st.rerun()
    
    if st.button("🗑️ Clear Document List", key="clear_docs_btn"):
        st.session_state.documents = []
        st.rerun()
    
    # Load documents on tab activation or button click
    if not st.session_state.documents:
        with st.spinner("Loading documents..."):
            try:
                response = requests.get(f"{API_BASE_URL}/documents/")
                
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.documents = data.get("documents", [])
                else:
                    st.error(f"Failed to load documents: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    if st.session_state.documents:
        st.info(f"Found {len(st.session_state.documents)} documents")
        
        for i, doc in enumerate(st.session_state.documents):
            with st.expander(f"Document {i+1}: {doc['id'][:20]}... - {doc['metadata'].get('topic', 'No topic')}", 
                           expanded=i==0):
                st.write(f"**Content:**")
                st.write(doc['content'])
                st.write(f"**Metadata:** {doc['metadata']}")
                st.write(f"**Created:** {doc.get('created_at', 'Unknown')}")
                
                # Delete button
                if st.button(f"Delete Document {i+1}", key=f"del_{doc['id']}"):
                    try:
                        response = requests.delete(f"{API_BASE_URL}/documents/{doc['id']}")
                        if response.status_code == 200:
                            st.success("Document deleted successfully!")
                            # Remove from local cache
                            st.session_state.documents = [d for d in st.session_state.documents if d['id'] != doc['id']]
                            st.rerun()
                        else:
                            st.error(f"Delete failed: {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        st.info("No documents found. Add some documents or seed the database.")

# IMPORTANT: Chat input must be at the VERY END, outside all tabs, columns, expanders
# Place this at the bottom of the file, after all other Streamlit elements

# Chat input - This should be the last Streamlit element
prompt = st.chat_input("Ask about cascade policies or renewable energy...")

if prompt:
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get response from API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/chat/",
                    json={"query": prompt, "top_k": 3}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer received")
                    
                    # Display answer
                    st.write(answer)
                    
                    # Display sources if available
                    if data.get("retrieved_documents"):
                        with st.expander("📚 Sources Used"):
                            for i, doc in enumerate(data.get("retrieved_documents", [])):
                                st.markdown(f"**Source {i+1}**")
                                st.markdown(f"**ID:** `{doc['id'][:20]}...`")
                                st.markdown(f"**Content:** {doc['content'][:300]}...")
                                if doc.get('distance'):
                                    st.markdown(f"**Relevance Score:** {(1 - doc['distance']):.3f}")
                                st.divider()
                    
                    # Add to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": data.get("retrieved_documents", [])
                    })
                else:
                    error_msg = f"Failed to get response from server: {response.status_code}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": error_msg
                })
    
    # Rerun to update the chat display
    st.rerun()