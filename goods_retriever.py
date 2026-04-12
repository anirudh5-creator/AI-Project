import pandas as pd
from sentence_transformers import SentenceTransformer, util


class GoodsRetriever:
    def __init__(self, csv_path):
        
        self.df = pd.read_csv(csv_path)

        if "Description of Goods" not in self.df.columns:
            raise Exception("❌ 'Description of Goods' column not found")

        self.text_column = "Description of Goods"

        
        self.df[self.text_column] = (
            self.df[self.text_column]
            .fillna('')
            .astype(str)
            .str.lower()
        )

        
        self.df = self.df[
            ~self.df[self.text_column].str.contains("nil", case=False, na=False)
        ]

        self.df = self.df[
            ~self.df[self.text_column].str.contains("all goods", case=False, na=False)
        ]

        
        self.df["search_text"] = self.df[self.text_column]

        
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        
        print("🔄 Encoding goods descriptions...")
        self.embeddings = self.model.encode(
            self.df["search_text"].tolist(),
            convert_to_tensor=True
        )

    def get_top_k(self, query, k=5):
        query = query.lower().strip()

        
        exact_matches = self.df[
            self.df["search_text"].str.contains(query, na=False)
        ]

        if len(exact_matches) > 0:
            results = []
            for _, row in exact_matches.head(k).iterrows():
                results.append({
                    "text": row[self.text_column],
                    "row": row
                })
            return results

        
        query_emb = self.model.encode(query, convert_to_tensor=True)

        hits = util.semantic_search(query_emb, self.embeddings, top_k=k)[0]

        results = []
        for hit in hits:
            row = self.df.iloc[hit['corpus_id']]

            results.append({
                "text": row[self.text_column],
                "row": row
            })

        return results