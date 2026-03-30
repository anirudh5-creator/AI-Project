import faiss
import numpy as np
import pickle

class VectorStore:
    def __init__(self, dim):
        self.index = faiss.IndexFlatL2(dim)
        self.texts = []

    def add(self, embeddings, texts):
        self.index.add(np.array(embeddings))
        self.texts.extend(texts)

    def search(self, query_embedding, k=3):
        D, I = self.index.search(query_embedding, k)
        return [self.texts[i] for i in I[0]]

    def save(self):
        with open("vector_store.pkl", "wb") as f:
            pickle.dump((self.index, self.texts), f)

    def load(self):
        with open("vector_store.pkl", "rb") as f:
            self.index, self.texts = pickle.load(f)