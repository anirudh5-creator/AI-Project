import pandas as pd
import numpy as np
import re
from sentence_transformers import SentenceTransformer, util


# 🔹 Preprocess query (IMPORTANT FIX)
def preprocess_query(query):
    numbers = re.findall(r'\d+', query)
    price = int(numbers[0]) if numbers else None
    clean_query = re.sub(r'\d+', '', query).strip()
    return clean_query, price


class GSTRetriever:
    def __init__(self, csv_path):
        # Load data
        self.df = pd.read_csv(csv_path)

        # Load model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        # Store descriptions
        self.descriptions = self.df['Description of Service'].astype(str).tolist()

        # Precompute embeddings
        print("🔄 Encoding service descriptions...")
        self.embeddings = self.model.encode(self.descriptions, convert_to_tensor=True)

    # 🔥 FIXED METHOD (proper indentation)
    def get_top_k(self, query, k=3):
        query_text, _ = preprocess_query(query)

        if not query_text:
            return []

        query_embedding = self.model.encode(query_text, convert_to_tensor=True)

        scores = util.cos_sim(query_embedding, self.embeddings)[0]

        top_k = min(k, len(scores))
        top_indices = scores.topk(top_k).indices.tolist()

        results = []
        for idx in top_indices:
            row = self.df.iloc[idx]

            results.append({
                "text": row['Description of Service'],  # ✅ required
                "row": row                              # ✅ full data
            })

        return results

    def retrieve(self, query):
        try:
            query_text, price = preprocess_query(query)

            if not query_text:
                return "❌ Please enter a valid service description."

            query_embedding = self.model.encode(query_text, convert_to_tensor=True)
            scores = util.cos_sim(query_embedding, self.embeddings)[0]

            best_idx = int(np.argmax(scores))
            best_score = float(scores[best_idx])

            if best_score < 0.3:
                return "❌ Could not determine best service category."

            row = self.df.iloc[best_idx]
            description = row['Description of Service']

            if 'GST Rate' in self.df.columns:
                gst_rate = float(row['GST Rate'])
            elif 'IGST Rate' in self.df.columns:
                gst_rate = float(row['IGST Rate'])
            else:
                gst_rate = 18.0

            if price:
                gst_amount = (price * gst_rate) / 100
                total = price + gst_amount

                return (
                    f"✅ Service: {description}\n"
                    f"💰 Price: ₹{price}\n"
                    f"📊 GST Rate: {gst_rate}%\n"
                    f"🧾 GST Amount: ₹{gst_amount:.2f}\n"
                    f"💵 Total Amount: ₹{total:.2f}"
                )
            else:
                return (
                    f"✅ Service: {description}\n"
                    f"📊 GST Rate: {gst_rate}%\n"
                    f"ℹ️ (Enter price to calculate GST amount)"
                )

        except Exception as e:
            return f"❌ Error: {str(e)}"