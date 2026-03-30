from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY")

def generate_answer(query, context):
    prompt = f"""
You are a GST expert.

Context:
{context}

Question:
{query}

Give:
- GST rate
- Explanation
"""

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content