import subprocess

def generate_response(query, category, rate, price, gst_amount, final_price):
    prompt = f"""
User Query: {query}

GST Info:
Category: {category}
GST Rate: {rate}%

Base Price: {price}
GST Amount: {gst_amount}
Final Price: {final_price}

Explain clearly how GST is applied.
"""

    result = subprocess.run(
        ["ollama", "run", "mistral"],
        input=prompt.encode(),
        stdout=subprocess.PIPE
    )

    return result.stdout.decode()