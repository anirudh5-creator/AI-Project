from sentence_transformers import SentenceTransformer
from embeddings.vector_store import VectorStore
from rag.llm import generate_answer

model = SentenceTransformer('all-MiniLM-L6-v2')

vs = VectorStore(dim=384)
vs.load()

def query_system(query):
    q_emb = model.encode([query])

    results = vs.search(q_emb, k=3)

    context = "\n".join(results)

    return generate_answer(query, context)