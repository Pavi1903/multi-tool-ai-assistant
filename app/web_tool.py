import time

def web_search_func(query: str) -> str:
    for attempt in range(3):
        try:
            from ddgs import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            if results:
                return "\n\n".join([
                    f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}"
                    for r in results
                ])
            print(f"[WEB]: Empty results on attempt {attempt + 1}")
            time.sleep(2)
        except Exception as e:
            print(f"[WEB ERROR attempt {attempt+1}]: {str(e)}")
            time.sleep(3)

    return "DDGSEARCH_FAILED"


def web_search_func_groq_fallback(client, query: str) -> str:
    """Use Groq LLM knowledge directly when web search fails."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a knowledgeable assistant. Answer the question directly and concisely from your own knowledge in 3-5 sentences."
            },
            {"role": "user", "content": query}
        ],
        max_tokens=512,
        temperature=0
    )
    return response.choices[0].message.content