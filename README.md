# 🤖 NexaCloud Persona-Adaptive Customer Support Agent

> An intelligent AI-powered customer support agent that automatically detects customer personas, retrieves relevant knowledge base content, adapts response tone, and escalates to human agents when needed.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.2+-green.svg)](https://langchain.com)
[![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-orange.svg)](https://ai.google.dev)
[![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://chromadb.com)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Architecture Diagram](#architecture-diagram)
4. [Persona Detection Strategy](#persona-detection-strategy)
5. [RAG Pipeline Design](#rag-pipeline-design)
6. [Escalation Logic](#escalation-logic)
7. [Setup Instructions](#setup-instructions)
8. [Environment Variables](#environment-variables)
9. [Example Queries](#example-queries)
10. [Project Structure](#project-structure)
11. [Known Limitations](#known-limitations)

---

## 📖 Project Overview

The NexaCloud Support Agent is a production-ready AI customer support system that:

- **Detects** 3 customer personas (Technical Expert, Frustrated User, Business Executive) using a hybrid rule-based + LLM approach
- **Retrieves** relevant support articles from a 15-document knowledge base using RAG (Retrieval-Augmented Generation)
- **Adapts** response tone, structure, and depth based on the detected persona
- **Escalates** to human agents automatically with a structured JSON handoff summary
- **Provides** a polished Streamlit web UI with dark-mode glassmorphism design AND a rich CLI interface

The system is grounded entirely in the knowledge base — it explicitly avoids hallucination by only responding based on retrieved content.

**Domain:** SaaS Product Support (fictional product: NexaCloud)

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.11+ | Core runtime |
| **LLM** | Google Gemini 1.5 Flash | Latest | Persona detection + response generation |
| **Embeddings** | Google `embedding-001` | Latest | Document and query embedding |
| **Fallback Embeddings** | Sentence Transformers `all-MiniLM-L6-v2` | 3.0+ | If no API key |
| **Vector DB** | ChromaDB | 0.5+ | Embedding storage + similarity search |
| **Agent Framework** | LangChain | 0.2+ | Document loading, chunking, retrieval |
| **Web UI** | Streamlit | 1.35+ | Interactive chat interface |
| **CLI** | Rich | 13.7+ | Formatted terminal output |
| **PDF Generation** | ReportLab | 4.0+ | Knowledge base PDF creation |
| **Env Management** | python-dotenv | 1.0+ | API key loading |

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                          │
│         ┌─────────────────┐    ┌──────────────────┐            │
│         │  Streamlit UI   │    │    Rich CLI       │            │
│         │ (ui/streamlit_  │    │ (cli/chat_cli.py) │            │
│         │    app.py)      │    │                   │            │
│         └────────┬────────┘    └────────┬──────────┘            │
└──────────────────┼──────────────────────┼────────────────────────┘
                   │                      │
                   ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATION                            │
│                                                                   │
│   User Message                                                    │
│       │                                                           │
│       ▼                                                           │
│  ┌─────────────────────┐                                         │
│  │  Persona Detector   │ ← Two-pass: Rule-based + Gemini LLM    │
│  │  (persona_detector) │   Output: Persona + Confidence Score    │
│  └──────────┬──────────┘                                         │
│             │                                                     │
│             ▼                                                     │
│  ┌─────────────────────┐                                         │
│  │    RAG Pipeline     │ ← ChromaDB similarity_search_with_score │
│  │  (rag_pipeline.py)  │   Output: Top-K chunks + scores         │
│  └──────────┬──────────┘                                         │
│             │                                                     │
│             ▼                                                     │
│  ┌─────────────────────┐                                         │
│  │  Escalation Handler │ ← 7 configurable triggers               │
│  │  (escalation_       │   Output: Should escalate? + reason     │
│  │   handler.py)       │                                         │
│  └──────────┬──────────┘                                         │
│             │                                                     │
│      ┌──────┴──────┐                                             │
│      │             │                                             │
│   Escalate?      Generate                                        │
│      │           Response                                        │
│      ▼             ▼                                             │
│  ┌────────┐  ┌─────────────────────┐                            │
│  │Handoff │  │  Response Generator │ ← Persona-specific prompts │
│  │Summary │  │ (response_generator)│   Grounded in KB content   │
│  └────────┘  └─────────────────────┘                            │
│                                                                   │
│  ┌─────────────────────┐                                         │
│  │  Conversation Memory│ ← Multi-turn context, sentiment tracking│
│  │  (conversation_     │                                         │
│  │   memory.py)        │                                         │
│  └─────────────────────┘                                         │
└─────────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE BASE LAYER                           │
│                                                                   │
│   /data/                                                          │
│   ├── saas_api_guide.pdf         (API Reference — PDF)           │
│   ├── password_reset_guide.md    (Account recovery)              │
│   ├── billing_policy.md          (Billing & payments)            │
│   ├── account_management.md      (Users & roles)                 │
│   ├── troubleshooting_guide.md   (Common issues)                 │
│   ├── sla_and_uptime.md          (SLA commitments)               │
│   ├── onboarding_guide.md        (Getting started)               │
│   ├── integrations_guide.md      (Third-party integrations)      │
│   ├── data_security_policy.md    (GDPR, SOC2, encryption)        │
│   ├── error_codes_reference.md   (API error codes)               │
│   ├── subscription_plans.md      (Plans & pricing)               │
│   ├── refund_policy.md           (Refund eligibility)            │
│   ├── two_factor_auth.md         (2FA setup)                     │
│   ├── webhook_documentation.md   (Webhook setup)                 │
│   └── rate_limiting_guide.md     (API rate limits)               │
│                                                                   │
│   ChromaDB vector store (./chroma_db/)                           │
│   • 800-char chunks with 120-char overlap                        │
│   • Google embedding-001 model                                   │
│   • Metadata: source_file, page_or_section, article_id           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎭 Persona Detection Strategy

### Overview

The system uses a **two-pass hybrid approach** for persona classification:

#### Pass 1: Rule-Based Keyword Analysis (Fast)
- 40+ technical keywords (API, SDK, JWT, OAuth, rate limit, stack trace...)
- 30+ frustration signals (emotional language, "nothing works", all-caps, "!!!")
- 25+ executive keywords (business impact, ROI, SLA, timeline, operations...)
- Scoring: count matches per category → argmax = initial persona
- Special boosts: multiple all-caps words (+2 frustrated), repeated `!` (+1 frustrated)

#### Pass 2: LLM Classification (Accurate)
- Sends message + conversation history to Gemini 1.5 Flash
- Structured JSON output: `{ "persona": "...", "confidence": 0.0-1.0, "reasoning": "..." }`
- Temperature set to 0.1 for consistent classification

#### Hybrid Decision Logic
```
IF llm_confidence >= 0.65:
    Use LLM persona
ELIF llm_persona != rule_persona:
    Use rule_persona (trust keyword signals when LLM uncertain)
    Set confidence = 0.6
ELSE:
    Both agree → use LLM result
```

#### Fallback
If LLM is unavailable: use rule-based only with confidence = `min(0.5 + signals × 0.08, 0.85)`

### Prompt Design
The classification prompt includes:
- Clear persona definitions with example phrases
- Last 4 turns of conversation history for context
- Explicit instructions to return ONLY valid JSON
- Validation of response structure before accepting

---

## 📚 RAG Pipeline Design

### Chunking Strategy
- **Splitter:** `RecursiveCharacterTextSplitter`
- **Chunk size:** 800 characters (balances context completeness vs retrieval precision)
- **Overlap:** 120 characters (ensures boundary sentences aren't split)
- **Separators:** `["\n\n", "\n", ".", "!", "?", ",", " "]` — hierarchical, preserving sentence structure

### Embedding Model
- **Primary:** Google `embedding-001` (via `langchain-google-genai`)
- **Fallback:** `sentence-transformers/all-MiniLM-L6-v2` — works without API key
- Chosen for: semantic understanding superior to BM25/TF-IDF, free tier availability

### Vector Database
- **ChromaDB** — persistent local store in `./chroma_db/`
- Chosen for: zero infrastructure, Python-native, excellent LangChain integration
- Collection metadata per chunk: `source_file`, `page_or_section`, `article_id`

### Retrieval Strategy
- **Method:** `similarity_search_with_score()` — returns L2 distance
- **Score conversion:** `similarity = 1 / (1 + L2_distance)` → normalized 0-1
- **Top-K:** 4 chunks (configurable in `app/config.py`)
- **Confidence threshold:** Score ≥ 0.40 = confident retrieval; below → triggers escalation consideration

### Document Loading
| Format | Loader | Metadata Extracted |
|---|---|---|
| `.pdf` | `PyPDFLoader` | Page number |
| `.md` | `TextLoader` | First `#` heading as section |
| `.txt` | `TextLoader` | "Section 1" (generic) |

---

## 🚨 Escalation Logic

### Trigger Conditions (evaluated in priority order)

| # | Trigger | Code | Priority | Description |
|---|---|---|---|---|
| 1 | Explicit user request | `EXPLICIT_REQUEST` | P1 | Keywords: "talk to human", "speak to agent", "escalate", etc. |
| 2 | Sensitive topic + low confidence | `SENSITIVE_TOPIC` | P1 | Billing/legal/security keywords + retrieval score < 0.40 |
| 3 | No relevant context found | `NO_CONTEXT` | P2 | Empty retrieval results (after first turn) |
| 4 | Consecutive low-confidence turns | `LOW_CONFIDENCE_STREAK` | P2 | 2+ consecutive turns below confidence threshold |
| 5 | Repeated frustration signals | `FRUSTRATED_ESCALATION` | P2 | 3+ turns with negative sentiment detected |
| 6 | Conversation turn limit | `TURN_LIMIT` | P3 | > 6 total user turns without resolution |
| 7 | Response not grounded | `GROUNDING_FAILURE` | P2 | Agent couldn't use KB, turn ≥ 2 |

### Confidence Thresholds (configurable in `app/config.py`)
```python
min_similarity_score = 0.40          # Below this = low retrieval confidence
max_low_confidence_turns = 2         # Consecutive low-confidence turns before escalation
max_conversation_turns = 6           # Total turns before suggesting escalation
max_frustrated_turns = 3             # Frustrated turns before escalation
```

### Handoff Summary Structure
```json
{
  "escalation_timestamp": "2025-06-15T14:30:00",
  "session_id": "20250615_143000",
  "priority": "P2",
  "escalation_trigger": "LOW_CONFIDENCE_STREAK",
  "persona": {
    "detected": "Technical Expert",
    "all_turns": [{"turn": 1, "persona": "Technical Expert", "confidence": 0.91}]
  },
  "issue": {
    "summary": "API authentication failure with 401 error on POST /v1/projects",
    "total_exchanges": 3
  },
  "knowledge_base": {
    "documents_referenced": ["error_codes_reference.md", "saas_api_guide.pdf"]
  },
  "attempted_steps": ["Check Authorization header format", "Verify API key is not expired"],
  "recommendation": "Review system logs for AUTH_002 error pattern",
  "route_to": "Level 2 Technical Support",
  "conversation_history": [...]
}
```

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.11 or higher
- Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com/app/apikey))
- Git

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd "Adsparkx AI Assignment"
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Keys
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_key_here
```

### Step 5: Generate the PDF Knowledge Base Document
```bash
python create_pdf.py
```
This generates `data/saas_api_guide.pdf` — the required PDF document.

### Step 6: Ingest Documents
```bash
python ingest.py
```
This loads all 15 documents, creates chunks, generates embeddings, and stores them in ChromaDB.

Expected output:
```
  ✅ Documents loaded: 15
  ✅ Chunks created:  ~180
  ✅ Time elapsed: ~60s
```

### Step 7: Launch the Application

**Web UI (Recommended):**
```bash
streamlit run ui/streamlit_app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

**CLI:**
```bash
python cli/chat_cli.py
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | **Yes** | Google Gemini API key. Free at [aistudio.google.com](https://aistudio.google.com/app/apikey) |
| `DEBUG` | No | Set to `true` for verbose logging. Default: `false` |

---

## 💬 Example Queries

### 1. Technical Expert — API Authentication
```
Can you explain the API authentication failure with error AUTH_002? 
I need the root cause and the exact header format required.
```
**Expected:** Detailed technical explanation with header format, error code meaning, and step-by-step fix.

### 2. Frustrated User — Password Reset
```
I've tried resetting my password 5 times and NOTHING WORKS!!! 
I'm locked out of my account! This is unacceptable!!!
```
**Expected:** Empathetic opener, simple step-by-step instructions, reassurance.

### 3. Business Executive — SLA Impact
```
Our team is unable to access the platform. What's the SLA impact 
and when will this be resolved?
```
**Expected:** Concise SLA summary, uptime commitments, resolution timeline, contact escalation path.

### 4. Technical Expert — Webhook Security
```
How do I implement HMAC-SHA256 signature verification for incoming webhooks?
```
**Expected:** Code example in Python/JavaScript, exact header name, security best practices.

### 5. Frustrated User — Billing Overcharge
```
I was charged twice this month! This is completely wrong!
```
**Expected:** Empathetic response, escalation triggered (billing + sensitive topic), handoff summary.

### 6. Business Executive — Subscription Comparison
```
Give me a high-level summary of what the Business plan includes 
versus Professional. What's the ROI justification?
```
**Expected:** Concise table/bullet comparison, business-impact framing.

### 7. Escalation Trigger
```
I need to speak to a human agent immediately about my account.
```
**Expected:** Immediate escalation, P1 priority, full handoff summary.

---

## 📁 Project Structure

```
Adsparkx AI Assignment/
├── app/
│   ├── __init__.py
│   ├── config.py              # All configurable settings
│   ├── persona_detector.py    # Two-pass persona classification
│   ├── rag_pipeline.py        # Document loading, chunking, retrieval
│   ├── response_generator.py  # Persona-specific response generation
│   ├── escalation_handler.py  # Escalation logic + handoff summary
│   └── conversation_memory.py # Multi-turn memory management
├── data/
│   ├── saas_api_guide.pdf     # API Reference (PDF — generated)
│   ├── password_reset_guide.md
│   ├── billing_policy.md
│   ├── account_management.md
│   ├── troubleshooting_guide.md
│   ├── sla_and_uptime.md
│   ├── onboarding_guide.md
│   ├── integrations_guide.md
│   ├── data_security_policy.md
│   ├── error_codes_reference.md
│   ├── subscription_plans.md
│   ├── refund_policy.md
│   ├── two_factor_auth.md
│   ├── webhook_documentation.md
│   └── rate_limiting_guide.md
├── ui/
│   └── streamlit_app.py       # Streamlit web UI
├── cli/
│   └── chat_cli.py            # Rich CLI interface
├── chroma_db/                 # Auto-generated ChromaDB storage
├── create_pdf.py              # PDF knowledge base generator
├── ingest.py                  # Document ingestion script
├── requirements.txt
├── .env.example               # Environment variables template
├── .gitignore
└── README.md
```

---

## ⚠️ Known Limitations

1. **LLM Cost:** Google Gemini free tier has rate limits (15 RPM). Heavy usage may hit limits.

2. **PDF Parsing Quality:** Complex PDF layouts with tables/images may not parse perfectly. Simple text-heavy PDFs work best.

3. **Single Session Memory:** Conversation history lives in memory — not persisted across server restarts. A database backend (SQLite/PostgreSQL) would enable persistence.

4. **Retrieval for Very Short Queries:** Very short or ambiguous queries (e.g., "help") may retrieve low-confidence results. Adding a query expansion step would improve this.

5. **Language Support:** Currently English-only. Multi-language support would require multilingual embeddings.

6. **No Authentication:** The web UI has no user authentication — suitable for internal demos. Production use requires auth.

7. **Knowledge Base Freshness:** Documents must be manually updated and re-ingested. A live API ingestion pipeline would keep KB current automatically.

### Future Improvements

- **LangGraph:** Replace linear pipeline with a stateful LangGraph workflow with conditional branching
- **Agentic Tools:** Add web search, live status page query, ticket creation as agent tools
- **Multi-language:** Support regional languages via multilingual embeddings
- **Analytics Dashboard:** Real-time metrics on persona distribution, escalation rates, satisfaction
- **Feedback Loop:** Thumbs up/down on responses to fine-tune retrieval and generation
- **Persistent Storage:** SQLite/PostgreSQL for conversation history across sessions
- **Confidence Calibration:** Fine-tune confidence thresholds based on real-world usage data

---

## 📄 License

This project was built as part of an AI Engineering internship assignment for Adsparkx.

---

*Built with ❤️ using Google Gemini, LangChain, ChromaDB, and Streamlit.*
