# 📚 ScholarGPT

ScholarGPT is a production-ready, zero-cost Retrieval-Augmented Generation (RAG) workspace designed to extract precise insights from dense scientific literature. By leveraging LangChain, Streamlit, and an in-memory ChromaDB vector store, the application creates an isolated semantic search matrix for any uploaded PDF, allowing users to execute deterministic Q&A without data persistence or cloud-hosting overhead.

---

## 🛠️ Tech Stack & Architecture

- **Orchestration:** LangChain Expression Language (LCEL)
- **Vector Database:** ChromaDB (Transient, running entirely in-memory per user session)
- **Embeddings Model:** Google AI Studio `gemini-embedding-001`
- **Generative LLM:** Google AI Studio `gemini-2.0-flash` (Configured at `temperature=0` for anti-hallucination guardrails)

---

## 🚀 Key Features

* **Zero-Cost Infrastructure:** Runs entirely inside free developer tiers and local server memory.
* **Transient Data Lifecycle:** Uploaded documents are parsed, chunked, and indexed on-the-fly. No data is written to permanent storage, ensuring absolute session privacy.
* **Recursive Parsing:** Leverages a `RecursiveCharacterTextSplitter` configured for a 1,000-character chunk size and 200-character overlap to preserve semantic context across multi-column academic layouts.
* **Rate-Limit Safeguards:** Implements Streamlit form barriers to freeze execution during active typing, preventing rapid keystroke script refreshes from exhausting API quotas.

---

## 📂 Project Structure

```text
scholar_gpt/
│
├── .env                # Local API Keys (Excluded from version control)
├── .gitignore          # Git exclusion rules 
├── requirements.txt    # Frozen python package dependencies
├── backend.py          # Vector pipeline, LCEL chains, and ingestion logic
└── app.py              # Reactive UI layout and state management engine
```


---

## ⚙️ Local Installation & Setup

1. Clone the Workspace

```
git clone https://github.com/PiyushWithPant/ScholarGPT.git
```

Go to the root dir

```
cd scholar-gpt
```

2. Create virtual env

```
python -m venv env
```

2. Activate env 

- On MacOS
```
source env/bin/activate
```

- On Windows

```
env\Scripts\activate
```

3. Install all dependencies

```
pip install -r requirements.txt
```


4. Configure Environment Secrets

```
GOOGLE_API_KEY="YourSecretKey..."
```

5. Launch the streamlit server

```
streamlit run app.py
```

---


## ⚖️ License
Distributed under the MIT License. See `LICENSE` for more information.


---

> By Piyush Pant (पियुष पंत)