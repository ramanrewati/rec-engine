# SHL Semantic Reasoning Assistant

> A next-gen AI-powered assistant that thinks before it speaks — designed to reason, retrieve, and respond with unmatched accuracy.

---

## Demo

**Live Demo:** [Click here to experience it!](https://shl-rec-engine.streamlit.app/)
*Note: The app is hosted on a serverless instance. It may take up to 50 seconds to load on a cold start.*

---

## Overview

This project combines retrieval-augmented generation and reflection-based reasoning to build a **logic-first, hallucination-free** AI assistant capable of intelligent Q&A over SHL knowledge base articles.
It scrapes, understands, and reflects before responding.

---

## Key Features

* **SHL Knowledge Base Integration**
  Scrapes and structures SHL documentation into markdown using `crawl4ai` for optimal LLM parsing.

* **Semantic Search with FAISS and HuggingFace**
  Uses high-quality embeddings for lightning-fast and meaningful document retrieval.

* **Gemini-Powered Reasoning**
  Backed by Google’s Gemini model and handcrafted reasoning prompts to ensure precision and minimal hallucination.

* **Dynamic Link Attestation**
  Query inputs are scanned for URLs, which are scraped and processed in real-time to enrich answers with verified data.

* **Chained Query Architecture**
  Input → Retrieval → Prompt Logic → Response — fully orchestrated using LangChain and LlamaIndex.

* **Interactive Streamlit UI**
  Built for clarity and performance. Deployed on Render for seamless public access.

---

## Tech Stack

| Layer               | Technology                      |
| ------------------- | ------------------------------- |
| **LLM**             | Google Gemini                   |
| **Vector Store**    | FAISS                           |
| **Embedding Model** | HuggingFace Inference API       |
| **Frameworks**      | LangChain, LlamaIndex           |
| **Scraper**         | crawl4ai                        |
| **Frontend**        | Streamlit                       |
| **Deployment**      | Render                          |
| **Environment**     | Python 3.12, uv package manager |


---

## Feedback & Contributions

Have ideas or suggestions? Open an issue or drop a star if you find this project valuable.

---

## License

This project is open-sourced under the MIT License.
