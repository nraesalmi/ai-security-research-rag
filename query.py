#!/usr/bin/env python3
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

os.environ["HF_TOKEN"] = os.environ.get("HF_TOKEN", "")

BASE_URL = os.environ.get("OPENROUTER_BASE_URL")
MODEL = "openai/gpt-4.1-mini"

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def load_vector_store(path="faiss_index"):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)


def retrieve_context(vector_store, query, k=5):
    docs = vector_store.similarity_search(query, k=k)
    return docs


def format_context(docs):
    context = ""
    for doc in docs:
        page_num = doc.metadata.get("page", "unknown")
        source = doc.metadata.get("source", "unknown")
        context += f"[Source: {source}, Page: {page_num}]\n{doc.page_content}\n\n"
    return context


def call_openai(messages):
    response = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": messages,
        },
    )
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
        response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


VECTOR_STORE = None


def get_vector_store():
    global VECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = load_vector_store()
    return VECTOR_STORE


ROUTER_SYSTEM_PROMPT = """You are a Router Agent that directs user questions to the most appropriate specialized agent.

You have four specialized agents available:
1. Methods Analyst - answers questions about methods/setup/dataset/metrics
2. Results Extractor - answers questions about results/numbers/ablations/comparisons
3. Skeptical Reviewer - answers questions about limitations/threats/critique
4. General Synthesizer - answers other questions

Analyze the user's question and respond with ONLY the name of the agent that should handle it.
Choose from: Methods Analyst, Results Extractor, Skeptical Reviewer, General Synthesizer

Respond with just the agent name, nothing else."""


def get_context_for_query(query):
    vector_store = get_vector_store()
    docs = retrieve_context(vector_store, query, k=5)
    return format_context(docs), docs


METHODS_ANALYST_SYSTEM_PROMPT = """You are a Methods Analyst Agent. Your role is to answer questions about research methods, experimental setup, datasets, and metrics.

When answering questions:
1. Use the provided context from the documents
2. Do NOT include any citations or references in your answer
3. Be precise and technical in your explanations

Context from documents:
{context}

Answer the user's question based on the provided context."""


RESULTS_EXTRACTOR_SYSTEM_PROMPT = """You are a Results Extractor Agent. Your role is to answer questions about experimental results, numbers, ablations, and comparisons.

When answering questions:
1. Extract specific numbers and statistics from the documents
2. Do NOT include any citations or references in your answer
3. Present results clearly with comparisons to baselines if available

Context from documents:
{context}

Answer the user's question based on the provided context."""


SKEPTICAL_REVIEWER_SYSTEM_PROMPT = """You are a Skeptical Reviewer Agent. Your role is to answer questions about limitations, threats to validity, critiques, and weaknesses of the research.

When answering questions:
1. Identify and discuss limitations mentioned in the documents
2. Do NOT include any citations or references in your answer
3. Be critical and objective in your analysis

Context from documents:
{context}

Answer the user's question based on the provided context."""


GENERAL_SYNTHESIZER_SYSTEM_PROMPT = """You are a General Synthesizer Agent. Your role is to answer general questions about the research that don't fit other categories.

When answering questions:
1. Synthesize information from multiple documents
2. Do NOT include any citations or references in your answer
3. Provide clear, comprehensive answers

Context from documents:
{context}

Answer the user's question based on the provided context."""


AGENT_PROMPTS = {
    "Methods Analyst": METHODS_ANALYST_SYSTEM_PROMPT,
    "Results Extractor": RESULTS_EXTRACTOR_SYSTEM_PROMPT,
    "Skeptical Reviewer": SKEPTICAL_REVIEWER_SYSTEM_PROMPT,
    "General Synthesizer": GENERAL_SYNTHESIZER_SYSTEM_PROMPT
}


def get_references(docs):
    seen = {}
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "unknown")
        if source not in seen:
            seen[source] = set()
        seen[source].add(page)
    
    references = []
    for source, pages in seen.items():
        sorted_pages = sorted(pages)
        if len(sorted_pages) == 1:
            references.append(f"{source}, page {sorted_pages[0]}")
        else:
            references.append(f"{source}, pages {', '.join(map(str, sorted_pages))}")
    
    return references


def route_question(question):
    context, docs = get_context_for_query(question)
    
    selected_agent_name = call_openai([
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": question}
    ]).strip()
    
    if selected_agent_name not in AGENT_PROMPTS:
        selected_agent_name = "General Synthesizer"
    
    system_prompt = AGENT_PROMPTS[selected_agent_name].format(context=context)
    
    answer = call_openai([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ])
    
    references = get_references(docs)
    
    return selected_agent_name, answer, references


def main():
    print("AI Security Research RAG - Query System")
    print("=" * 50)
    print("Ask questions about the research papers.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        try:
            print("Processing...")
            agent_name, answer, references = route_question(question)
            print(f"\n{agent_name}:")
            print(answer)
            print("\nReferences:")
            for ref in references:
                print(f"  - {ref}")
            print()
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    main()
