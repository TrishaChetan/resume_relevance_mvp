# embedder.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from config import SEMANTIC_MODEL

model = SentenceTransformer(SEMANTIC_MODEL)
index = None

def build_index(resume_texts):
    global index
    vectors = [model.encode(t) for t in resume_texts]
    dim = vectors[0].shape[0]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype('float32'))

def query_similarity(text):
    global index
    vec = model.encode([text]).astype('float32')
    D, I = index.search(np.array(vec), k=5)
    return I, D
