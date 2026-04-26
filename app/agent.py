import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

import groq
from app.rag_tool import rag_search
from app.web_tool import web_search_func

def create_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found.")
    return groq.Groq(api_key=api_key)


def is_rag_result_useful(result: str) -> bool:
    if not result:
        return False
    if "No relevant information" in result:
        return False
    if "failed" in result.lower():
        return False
    if len(result.strip()) < 80:
        return False
    return True


def generate_answer(client, user_query: str, tool_result: str) -> str:
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a precise, concise assistant. Answer the user's question "
                    "using ONLY the provided search results.\n"
                    "- Give a direct, clear answer in 3-5 sentences.\n"
                    "- Do NOT say 'based on the search results'.\n"
                    "- Do NOT speculate beyond what the results say.\n"
                    "- If the results do not contain enough information to answer, "
                    "reply with ONLY the word: INSUFFICIENT\n"
                    "- If from a document, mention the page number if available."
                )
            },
            {
                "role": "user",
                "content": f"Question: {user_query}\n\nSearch Results:\n{tool_result}"
            }
        ],
        max_tokens=512,
        temperature=0
    )
    return response.choices[0].message.content.strip()


def run_agent(client, user_query: str) -> tuple[str, str]:

    # Step 1: Always try RAG first
    rag_result = rag_search(user_query)
    print(f"[RAG]: {len(rag_result)} chars | {rag_result[:200]}")

    if is_rag_result_useful(rag_result):
        # Step 2: Try to generate answer from RAG
        answer = generate_answer(client, user_query, rag_result)
        print(f"[RAG ANSWER]: {answer[:100]}")

        # Step 3: If LLM says RAG result is insufficient, fall back to web
        if answer.strip().upper() == "INSUFFICIENT" or "INSUFFICIENT" in answer:
            print("[FALLBACK]: RAG insufficient → switching to web")
            web_result = web_search_func(user_query)
            tool_used = "🌐 Web Search (not in document)"
            answer = generate_answer(client, user_query, web_result)
        else:
            tool_used = "📄 Document RAG"
    else:
        # RAG found nothing at all → go straight to web
        print("[ROUTING]: RAG empty → web search")
        web_result = web_search_func(user_query)
        tool_used = "🌐 Web Search"
        answer = generate_answer(client, user_query, web_result)

    if not answer or "INSUFFICIENT" in answer:
        answer = "Could not find a good answer. Please try rephrasing."

    return answer, tool_used