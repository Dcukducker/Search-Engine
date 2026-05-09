import json
import os
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import re

class MultiFactorEngine:
    def __init__(self):
        self.papers = []
        self.bm25_engine = None
        self.semantic_model = None
        self.embeddings = None
        self.is_ready = False
        
    def load_and_index(self):
        print(">> Engine Init: Loading data...")
        if not os.path.exists('data/papers.json'):
            print(">> [Error] No data found. Please run data_collector.py first.")
            return
            
        with open('data/papers.json', 'r', encoding='utf-8') as f:
            self.papers = json.load(f)
            
        print(f">> Engine Init: Building Lexical Index (BM25) for {len(self.papers)} papers...")
        tokenized_corpus = [self._tokenize(p['title'] + " " + p['abstract']) for p in self.papers]
        self.bm25_engine = BM25Okapi(tokenized_corpus)
        
        print(">> Engine Init: Building Semantic Index (HuggingFace Transformers Vectors)...")
        # Load a lightweight model (Takes a bit of time to download on first run)
        self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        corpus_texts = [p['title'] + ". " + p['abstract'] for p in self.papers]
        self.embeddings = self.semantic_model.encode(corpus_texts, convert_to_numpy=True)
        
        print(">> Engine Init: Normalizing Embeddings for Cosine Similarity...")
        # Normalize embeddings to easily calculate cosine similarity via dot product
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norms[norms == 0] = 1e-10 
        self.embeddings = self.embeddings / norms
        
        self.is_ready = True
        print(">> Engine is Ready!")

    def _tokenize(self, text):
        # Simple lowercase tokenization based on non-word chars
        return [word for word in re.split(r'\W+', text.lower()) if word]

    def _normalize_scores(self, scores):
        scores = np.array(scores)
        if len(scores) == 0:
            return scores
        min_s, max_s = np.min(scores), np.max(scores)
        if max_s - min_s == 0:
            return np.zeros_like(scores)
        return (scores - min_s) / (max_s - min_s)

    def search(self, query: str, w_bm25=1.0, w_sem=1.0, w_auth=1.0, top_k=20):
        if not self.is_ready:
            return []
            
        # 1. Lexical Scoring (BM25)
        query_tokens = self._tokenize(query)
        bm25_scores = self.bm25_engine.get_scores(query_tokens)
        bm25_norm = self._normalize_scores(bm25_scores)
        
        # 2. Semantic Scoring (Cosine Similarity)
        query_emb = self.semantic_model.encode([query], convert_to_numpy=True)[0]
        query_norm_val = np.linalg.norm(query_emb)
        if query_norm_val > 0:
            query_emb = query_emb / query_norm_val
            
        # Cosine sim is dot product since both are normalized vectors
        sem_scores = np.dot(self.embeddings, query_emb)
        sem_norm = self._normalize_scores(sem_scores)
        
        # 3. Authority Scoring (Mocked PageRank)
        auth_scores = np.array([p.get('authority_score', 0) for p in self.papers])
        auth_norm = self._normalize_scores(auth_scores)
        
        results = []
        for i, paper in enumerate(self.papers):
            score_bm25 = float(bm25_norm[i])
            score_sem = float(sem_norm[i])
            score_auth = float(auth_norm[i])
            
            # Final Hybrid Scoring
            final_score = (w_bm25 * score_bm25) + (w_sem * score_sem) + (w_auth * score_auth)
            
            # Fast filter: skip items with practically 0 relevance mathematically
            if query_tokens and score_bm25 < 0.01 and score_sem < 0.1:
                continue 
                
            results.append({
                "paper": paper,
                "scores": {
                    "bm25": round(score_bm25, 4),
                    "semantic": round(score_sem, 4),
                    "authority": round(score_auth, 4),
                    "final": round(final_score, 4)
                }
            })
            
        # Sort by final score
        results.sort(key=lambda x: x['scores']['final'], reverse=True)
        return results[:top_k]
