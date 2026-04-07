import subprocess

def rewrite_query(query):
    prompt = f"""
Convert the query into a GST service phrase.

IMPORTANT:
- Preserve key meaning (passenger vs goods, food vs delivery, etc.)
- Be specific, not generic
- Do NOT lose important context

Examples:
- "flight ticket" → "air passenger transport service"
- "rail ticket" → "rail passenger transport service"
- "goods by train" → "transport of goods by rail"
- "pizza order" → "restaurant service"

Query: {query}

Output only the phrase.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20
        )

        rewritten = result.stdout.decode().strip()

        # fallback safety
        if len(rewritten) < 3:
            return query

        return rewritten

    except:
        return query