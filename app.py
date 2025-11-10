import os
import re
import streamlit as st
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding
from llama_index.core.prompts import PromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine

import scraping_utils


# --- ENV ---
load_dotenv()

hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable not found")

g_key = os.getenv("GEMINI_API_KEY")
if not g_key:
    raise ValueError("GEMINI_API_KEY environment variable not found")


# --- Streamlit page setup ---
st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
<style>
    .stApp { background-color: #121212; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    .stMarkdown h1 { color: #bb86fc; font-weight: 700; }
    .stTextArea textarea {
        border: 2px solid #bb86fc; border-radius: 8px; padding: 12px;
        background-color: #1e1e1e; color: #e0e0e0;
    }
    .stButton button {
        background-color: #6d2abf; color: white; border-radius: 8px;
        padding: 10px 24px; font-weight: 500; transition: all 0.3s;
    }
    .stButton button:hover { background-color: #985eff; transform: translateY(-2px); }
</style>
""",
    unsafe_allow_html=True,
)


# --- Load LlamaIndex-compatible index ---
def load_vector_store():
    persist_dir = "faiss_index"
    if not os.path.exists(persist_dir):
        st.error("Vector store not found. Please build it first.")
        return None

    try:
        # ensure we pass the same embed model used for building
        embed_model = HuggingFaceInferenceAPIEmbedding(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            api_key=hf_token,
        )

        vector_store = FaissVectorStore.from_persist_dir(persist_dir)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=persist_dir
        )

        # inject embed_model so it does not fallback to OpenAI
        index = load_index_from_storage(storage_context=storage_context, embed_model=embed_model)
        return index

    except Exception as e:
        st.error(f"Error loading FAISS index: {e}")
        return None


# --- Build Query Engine ---
def get_query_engine(index):
    # LLM
    llm = GoogleGenAI(
        model="gemini-2.0-flash-lite",
        api_key=g_key,
        temperature=0.2,
    )

    retriever = index.as_retriever(similarity_top_k=10)

    with open("sys2.md", "r") as f:
        SYSTEM_PROMPT = f.read()

    prompt = PromptTemplate(
        template=f"""{SYSTEM_PROMPT}

Context:
{{context_str}}

Query:
{{query_str}}

Response:"""
    )

    # use factory to construct engine with current API
    engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        text_qa_template=prompt,
        llm=llm,
    )

    return engine


# --- Process query ---
def process_query(query):
    urls = re.findall(r'(https?://\S+)', query)
    scraped_data = ""

    if urls:
        with st.status("Scraping linked content...", expanded=True):
            for url in urls:
                scraped = scraping_utils.scrape_url(url)
                scraped_data += f"\n\nScraped content from {url}:\n{scraped}"

    full_query = query + scraped_data

    with st.spinner("Analyzing request with SHL knowledge base..."):
        try:
            index = load_vector_store()
            if index is None:
                return "Error: Knowledge base not loaded"

            engine = get_query_engine(index)
            response = engine.query(full_query)
            return str(response)
        except Exception as e:
            st.error(f"Analysis error: {str(e)}")
            return None


# --- Render response ---
def render_response(response):
    if not response:
        return
    sections = re.findall(r'<(\w+)>([\s\S]*?)</\1>', response)
    if not sections:
        st.markdown(response)
        return
    sections = sorted(sections, key=lambda x: 0 if x[0].lower() == "result" else 1)
    tab_names = [sec[0].capitalize() for sec in sections]
    tabs = st.tabs(tab_names)
    for i, tab in enumerate(tabs):
        with tab:
            content = sections[i][1].strip()
            if sections[i][0].lower() == "result":
                st.markdown(content, unsafe_allow_html=True)
            else:
                st.markdown(
                    f"""
                <div style="background: #1e1e1e; padding: 16px; border-radius: 8px;
                            border-left: 4px solid #bb86fc; margin-bottom: 16px; color: #e0e0e0;">
                {content}
                </div>
                """,
                    unsafe_allow_html=True,
                )


# --- UI ---
st.title("SHL Assessment Recommendation System")
st.markdown(
    """
    <div style="background: #2c2c2c; padding: 16px; border-radius: 8px; margin-bottom: 24px;">
    <h3 style="color: #bb86fc; margin-top: 0;">AI-Powered Assessment Matching Engine</h3>
    <p>Describe your assessment needs and get personalized recommendations from SHL's product catalog.</p>
    </div>
""",
    unsafe_allow_html=True,
)

query = st.text_area(
    "Describe your assessment needs:",
    placeholder="e.g. 'I need cognitive ability tests under 45 minutes for remote hiring of financial analysts...'",
    height=150,
    key="query_input",
)

if st.button("Generate Recommendations", type="primary"):
    if not query:
        st.warning("Please enter your assessment requirements")
    else:
        response = process_query(query)
        if response:
            render_response(response)

            with st.expander("View raw LLM response"):
                st.text_area(
                    "Full Response:",
                    response,
                    height=300,
                )

