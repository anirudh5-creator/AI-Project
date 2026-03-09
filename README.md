
# GST RAG System (Retrieval-Augmented Generation)

An AI-powered system that answers GST-related queries by retrieving information from official GST documents and generating accurate explanations.

This project uses **OCR, document processing, vector embeddings, and retrieval-based generation** to provide reliable GST rate information.

---

# Project Overview

GST notifications, circulars, and rate documents are often stored as **PDF files** that are difficult to search programmatically.

This system converts those documents into a **searchable knowledge base** and allows users to ask questions like:

- What is the GST on laptops?
- GST rate for mobile phones
- Calculate final price including GST

The system retrieves relevant GST data and generates a clear response.

---

# System Workflow

OCR → Clean → Chunk → Embed → Store → Retrieve → Generate Answer

---

# Architecture

### Phase 1 – Data Collection
- Download GST notifications and circulars from official government websites
- Store PDF documents locally

### Phase 2 – Document Processing
- Convert scanned PDFs to images
- Apply OCR using **PaddleOCR / Tesseract**
- Clean extracted text
- Split documents into logical chunks

### Phase 3 – Data Storage
- Generate embeddings for each text chunk
- Store embeddings in **FAISS / Qdrant**
- Store structured data in **PostgreSQL**

### Phase 4 – Query Processing
When a user asks a question:

1. Convert query to embedding  
2. Retrieve relevant chunks from vector database  
3. Extract GST information  
4. Generate a clear answer  

### Phase 5 – User Output

Frontend displays:

- GST rate
- Final calculated price (if base price provided)
- Source reference
- Explanation

---

# Tech Stack

## Backend
- Python
- FastAPI / Flask

## OCR
- PaddleOCR
- Tesseract

## NLP / RAG
- Sentence Transformers
- LangChain

## Vector Database
- FAISS / Qdrant

## Database
- PostgreSQL

## Document Processing
- PyMuPDF
- pdf2image
- regex

---

# Features

- OCR support for scanned PDFs
- Automatic document chunking
- Vector search using FAISS
- Natural language query support
- Source citation for transparency
- GST price calculation

#  Author

**Anirudh Gowri Sankaran**
**Aadesh Kumar Yadav**
**Atharva Garg**
**Carolin Anto Vazhappilly**
**Bhavani Srinivasan**
