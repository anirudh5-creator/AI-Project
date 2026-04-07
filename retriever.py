import pandas as pd
import re
from sentence_transformers import SentenceTransformer, CrossEncoder, util

class GSTRetriever:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

        # Clean text
        self.df['search_text'] = self.df['Description of Service'].fillna('').astype(str).str.lower()

        # 🔥 Define models properly
        self.bi_encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

        # Precompute embeddings
        self.embeddings = self.bi_encoder.encode(
            self.df['search_text'].tolist(),
            convert_to_tensor=True
        )

    # -------------------------
    # Price Extraction
    # -------------------------
    def extract_price(self, text):
        text = text.lower().replace(',', '')

        lakh_match = re.search(r'(\d+(\.\d+)?)\s*lakh', text)
        if lakh_match:
            return float(lakh_match.group(1)) * 100000

        k_match = re.search(r'(\d+(\.\d+)?)\s*k', text)
        if k_match:
            return float(k_match.group(1)) * 1000

        raw_numbers = re.findall(r'\d{4,}', text)
        if raw_numbers:
            return float(raw_numbers[0])

        return None
    
    def get_top_k(self, query, k=5):
        query_emb = self.bi_encoder.encode(query, convert_to_tensor=True)

        hits = util.semantic_search(query_emb, self.embeddings, top_k=k)[0]

        results = []
        for hit in hits:
            row = self.df.iloc[hit['corpus_id']]
            results.append({
                "text": row['Description of Service'],
                "row": row
            })

        return results
    
        def get_top_k(self, query, k=5):
            query_emb = self.bi_encoder.encode(query, convert_to_tensor=True)

            hits = util.semantic_search(query_emb, self.embeddings, top_k=k)[0]

            results = []
            for hit in hits:
                row = self.df.iloc[hit['corpus_id']]
                results.append({
                    "text": row['Description of Service'],
                    "row": row
                })

            return results

    # -------------------------
    # Retrieval (Bi + Cross Encoder)
    # -------------------------
    def get_gst_info(self, query):
        query_emb = self.bi_encoder.encode(query, convert_to_tensor=True)

        hits = util.semantic_search(query_emb, self.embeddings, top_k=10)[0]

        candidates = [
            self.df.iloc[hit['corpus_id']]['search_text']
            for hit in hits
        ]

        model_inputs = [[query, cand] for cand in candidates]
        cross_scores = self.cross_encoder.predict(model_inputs)

        # Re-rank
        for i in range(len(hits)):
            hits[i]['score'] = cross_scores[i]

        hits = sorted(hits, key=lambda x: x['score'], reverse=True)
        best = hits[0]

        # 🔥 Threshold (important)
        if best['score'] < 0.3:
            return None

        row = self.df.iloc[best['corpus_id']]

        return {
            "description": row['Description of Service'],
            "cgst": row['CGST Rate (%)'],
            "sgst": row['SGST/UTGST Rate (%)'],
            "igst": row['IGST Rate (%)'],
            "chapter": row['Chapter / Section / Heading'],
            "condition": row.get('Condition', 'N/A')
        }