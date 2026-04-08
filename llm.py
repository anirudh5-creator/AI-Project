def generate_response(query, description, rate, price, gst_amount, total):
    import requests

    prompt = f"""
You are a GST expert for INDIA ONLY.

STRICT RULES:
- Only talk about Indian GST
- Do NOT mention any other country
- Use ONLY the given GST rate
- Do NOT guess or hallucinate
- Keep answer short and clear

Query: {query}

Service: {description}
GST Rate: {rate}%
Base Price: ₹{price}
GST Amount: ₹{gst_amount:.2f}
Total Price: ₹{total:.2f}

Explain the GST calculation briefly in 2-3 lines.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        )

        # 🔥 handle bad responses safely
        if response.status_code == 200:
            data = response.json()
            return data.get("response", "").strip()

        else:
            return "⚠️ LLM returned an unexpected response."

    except Exception:
        # 🔥 fallback (guaranteed working)
        return f"""
GST Calculation (India):

Base Price: ₹{price}
GST Rate: {rate}%

GST Amount = ₹{gst_amount:.2f}
Total Amount = ₹{total:.2f}
"""