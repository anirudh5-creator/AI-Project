from fastapi import FastAPI
from rag.query_engine import query_system

app = FastAPI()

@app.get("/ask")
def ask(query: str):
    answer = query_system(query)
    return {"answer": answer}