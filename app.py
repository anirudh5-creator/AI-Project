from ocr.ocr_pipeline import all_rows

from processing.build_dataset import build_dataset, save_dataset
from processing.chunker import chunk_data

from database.insert_data import create_table, insert_data

from embeddings.embedder import create_embeddings
from embeddings.vector_store import VectorStore

# 1. Build dataset
data = build_dataset(all_rows)
save_dataset(data)

# 2. Store in DB
create_table()
insert_data(data)

# 3. Chunking
chunks = chunk_data(data)

# 4. Embeddings
embeddings = create_embeddings(chunks)

# 5. FAISS
vs = VectorStore(dim=embeddings.shape[1])
vs.add(embeddings, chunks)
vs.save()

print("✅ SYSTEM READY")