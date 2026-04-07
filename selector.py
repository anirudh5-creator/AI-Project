import re
import subprocess

def select_best(query, candidates, mode="service"):
    options = ""
    for i, c in enumerate(candidates):
        options += f"{i+1}. {c['text']}\n"

    # 🔥 Mode-based rules
    if mode == "goods":
        extra_rules = """
IMPORTANT RULES:
- DO NOT choose generic entries like "Nil rate"
- Prefer specific product names over general categories
"""
    else:
        extra_rules = ""

    prompt = f"""
You are a GST expert.

Select the most relevant GST category for the query.

{extra_rules}

Query:
{query}

Options:
{options}

Return ONLY the option number (1, 2, 3, ...). Do not explain.
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "mistral"],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20
        )

        output = result.stdout.decode().strip()

        print("LLM RAW OUTPUT:", output)  # debug

        match = re.search(r'\d+', output)
        if not match:
            return None

        idx = int(match.group()) - 1

        if 0 <= idx < len(candidates):
            return candidates[idx]["row"]

    except Exception as e:
        print("Selector error:", e)

    return None