import os
import faiss
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter

from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding


# --- ENV ---
load_dotenv()
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable not found")


# --- Embedding model ---
embed_model = HuggingFaceInferenceAPIEmbedding(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    api_key=hf_token,
)


# --- Read and split markdown file ---
with open("data/shl-docs.md", "r") as f:
    markdown = f.read()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]
splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    return_each_line=False,
)
chunks = splitter.split_text(markdown)

# Convert chunks to LlamaIndex Documents
documents = [Document(text=chunk.page_content) for chunk in chunks]


# --- Create FAISS index ---
# 384 for MiniLM (use 1536 if text-embedding-ada-002)
d = 384
faiss_index = faiss.IndexFlatL2(d)
vector_store = FaissVectorStore(faiss_index=faiss_index)

# --- Create storage context ---
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# --- Build index ---
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    embed_model=embed_model,
)

# --- Persist index ---
os.makedirs("faiss_index", exist_ok=True)
index.storage_context.persist(persist_dir="faiss_index")

print("LlamaIndex FAISS index built and saved with markdown header chunking.")
