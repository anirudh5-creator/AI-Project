import pandas as pd
from sentence_transformers import SentenceTransformer, util

class GoodsRetriever:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)

        self.df['search_text'] = self.df.iloc[:, 0].fillna('').astype(str).str.lower()

        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        self.embeddings = self.model.encode(
            self.df['search_text'].tolist(),
            convert_to_tensor=True
        )

    def get_top_k(self, query, k=5):
        query_emb = self.model.encode(query, convert_to_tensor=True)

        hits = util.semantic_search(query_emb, self.embeddings, top_k=k)[0]

        results = []
        for hit in hits:
            row = self.df.iloc[hit['corpus_id']]
            results.append({
                "text": row.iloc[0],
                "row": row
            })

        return results