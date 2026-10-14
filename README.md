# ChatBot_In_LangGraph

**A progressive, hands-on series of chatbots built with LangGraph, starting from a basic streaming bot and growing into a memory-backed, tool-using, RAG-powered assistant.**

Each folder in this repo is a self-contained project that adds one production-style capability to the chatbot: streaming, short-term memory, resumable conversation threads, SQLite persistence, tools with observability, and retrieval-augmented generation (RAG).

---

## Overview

Building a chatbot that works in a demo is easy. Building one that **remembers context, survives restarts, calls tools, and answers from your own documents** takes a few extra layers.

This repo builds those layers one at a time using **LangGraph**, so each stage is small enough to understand on its own and the full progression shows how a real chatbot is put together.

## What's Inside

| # | Folder | What it demonstrates |
|---|---|---|
| 1 | `chatbot_streaming/` | Token-by-token streaming of LLM responses |
| 2 | `chatbot_shortTermMemory_StreamLit/` | Short-term conversation memory with a Streamlit chat UI |
| 3 | `Chatbot_ResumingChat_Thread_Feature/` | Multiple chat threads, with the ability to resume past conversations |
| 4 | `Chatbot_Connecting_SqliteDB./` | Persistent memory using a SQLite-backed LangGraph checkpointer |
| 5 | `Chatbot_Tools_Observability/` | Tool calling plus tracing/observability of agent runs |
| 6 | `chatbot_with_RAG/` | Answering questions from your own documents with RAG |

<!-- VERIFY: reorder rows to match the order you built them in -->

## Features

- **Streaming responses** for a responsive chat experience
- **Short-term memory** so the bot keeps context within a conversation
- **Thread management** to start new chats and resume old ones
- **Persistent storage** with SQLite, so conversations survive app restarts
- **Tool use** so the bot can call external functions when needed
- **Observability** to trace and debug each step of a graph run
- **RAG** to ground answers in your own documents
- **Streamlit UI** for a clean chat interface

## Architecture

All chatbots share the same core LangGraph pattern: a state graph whose state is the message history, with a checkpointer that saves state per thread.

```
  User message
       │
       ▼
┌──────────────────┐        ┌───────────────────────┐
│  Streamlit UI    │ ─────▶ │   LangGraph Graph     │
│  (thread_id)     │        │  State: messages[]    │
└──────────────────┘        └──────────┬────────────┘
       ▲                               │
       │                    ┌──────────┴──────────┐
       │                    ▼                     ▼
       │               Chat node           Tool node / Retriever
       │               (LLM call)          (tools or vector store)
       │                    │                     │
       │                    └──────────┬──────────┘
       │                               ▼
       │                    ┌──────────────────────┐
       └─────────────────── │ Checkpointer         │
         streamed reply     │ (in-memory → SQLite) │
                            └──────────────────────┘
```

**Key idea:** the `thread_id` identifies a conversation. The checkpointer stores the state for each thread, which is what makes memory and resumable chats possible.

## Project Structure

```
ChatBot_In_LangGraph/
├── chatbot_streaming/                    # Streaming responses
├── chatbot_shortTermMemory_StreamLit/    # Short-term memory + Streamlit UI
├── Chatbot_ResumingChat_Thread_Feature/  # Multi-thread / resume chats
├── Chatbot_Connecting_SqliteDB./         # SQLite persistence
├── Chatbot_Tools_Observability/          # Tools + observability
├── chatbot_with_RAG/                     # RAG over your documents
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python |
| Orchestration | LangGraph, LangChain |
| LLM | <!-- VERIFY: e.g. OpenAI / Groq --> |
| Frontend | Streamlit |
| Persistence | SQLite (LangGraph SQLite checkpointer) |
| Observability | <!-- VERIFY: e.g. LangSmith --> |
| RAG | <!-- VERIFY: embeddings + vector store, e.g. FAISS / Chroma --> |

## Prerequisites

- Python 3.10+
- An API key for your LLM provider
- An observability API key, if you use tracing <!-- VERIFY: e.g. LangSmith: https://smith.langchain.com -->

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/SyedaNaziaGit/ChatBot_In_LangGraph.git
cd ChatBot_In_LangGraph
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install langgraph langchain langchain-community langgraph-checkpoint-sqlite streamlit python-dotenv
```

<!-- VERIFY: add your LLM package (e.g. langchain-openai / langchain-groq) and RAG packages
     (e.g. faiss-cpu, pypdf). If a folder has its own requirements.txt, mention it here. -->

### 4. Configure environment variables

Create a `.env` file in the project root (or in the folder you're running):

```env
# Replace with the keys your chatbot actually uses
OPENAI_API_KEY=your_llm_api_key
LANGCHAIN_API_KEY=your_observability_key
```

>  Never commit your `.env` file. Add it to `.gitignore` before pushing.

## Running a Chatbot

Each folder is independent. Move into the one you want and run its entry file:

```bash
cd chatbot_shortTermMemory_StreamLit
streamlit run <your_app_file>.py
```

<!-- VERIFY: replace <your_app_file>.py with the real filename(s), and note which
     folders are notebooks/scripts instead of Streamlit apps -->

For the SQLite and thread-resume versions, the database file is created automatically on first run, so you can close the app and reopen it to see your previous chats.

## Key Concepts Covered

- **StateGraph and messages state:** representing a conversation as graph state
- **Streaming:** emitting tokens as they are generated instead of waiting for the full reply
- **Checkpointers:** saving graph state per thread, in memory first and then in SQLite
- **Thread IDs:** separating and resuming independent conversations
- **Tool calling:** letting the LLM decide when to call external functions
- **Observability and tracing:** inspecting each node, tool call, and LLM call in a run
- **RAG:** retrieving relevant chunks from documents and using them as context

---
