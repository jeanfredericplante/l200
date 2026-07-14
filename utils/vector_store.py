import math
import re

class LocalVectorStore:
    """
    A lightweight, pure-Python semantic vector store implementing a Term Frequency-Inverse Document Frequency (TF-IDF)
    vector space model with Cosine Similarity. Provides genuine semantic vector retrieval for grounding queries.
    """
    def __init__(self):
        self.documents = {}  # doc_id -> {"text": text, "metadata": metadata}
        self.vocab = set()
        self.idf = {}
        self.doc_vectors = {}  # doc_id -> term -> tf_idf

    def add_document(self, doc_id: str, text: str, metadata: dict = None):
        """Adds a document to the vector store and rebuilds the index."""
        self.documents[doc_id] = {"text": text, "metadata": metadata or {}}
        self._rebuild_index()

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize and normalize input string."""
        return re.findall(r'\w+', text.lower())

    def _rebuild_index(self):
        """Recomputes TF-IDF vectors for all indexed documents."""
        self.vocab = set()
        doc_tfs = {}

        # 1. Calculate Term Frequencies (TF)
        for doc_id, doc in self.documents.items():
            tokens = self._tokenize(doc["text"])
            tf = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
            doc_tfs[doc_id] = tf
            self.vocab.update(tf.keys())

        # 2. Calculate Document Frequencies (DF) & IDF
        num_docs = len(self.documents)
        df = {}
        for token in self.vocab:
            df[token] = sum(1 for d_id in self.documents if token in doc_tfs[d_id])
            self.idf[token] = math.log((1 + num_docs) / (1 + df[token])) + 1.0

        # 3. Build TF-IDF vectors
        self.doc_vectors = {}
        for doc_id, tf in doc_tfs.items():
            vector = {}
            for token, freq in tf.items():
                vector[token] = freq * self.idf[token]
            self.doc_vectors[doc_id] = vector

    def similarity_search(self, query: str, top_k: int = 3) -> list[dict]:
        """Performs vector similarity search using Cosine Similarity on TF-IDF vectors."""
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.documents:
            return []

        # 1. Build Query TF-IDF Vector
        query_tf = {}
        for token in query_tokens:
            query_tf[token] = query_tf.get(token, 0) + 1

        query_vector = {}
        for token, freq in query_tf.items():
            if token in self.idf:
                query_vector[token] = freq * self.idf[token]

        # 2. Calculate Cosine Similarities against all docs
        scores = []
        query_norm = math.sqrt(sum(v**2 for v in query_vector.values()))
        if query_norm == 0:
            return []

        for doc_id, doc_vector in self.doc_vectors.items():
            # Dot Product
            dot_product = sum(query_vector.get(t, 0) * doc_vector.get(t, 0) for t in query_vector if t in doc_vector)
            
            # Document Norm
            doc_norm = math.sqrt(sum(v**2 for v in doc_vector.values()))

            if doc_norm > 0:
                similarity = dot_product / (query_norm * doc_norm)
            else:
                similarity = 0.0

            scores.append((similarity, doc_id))

        # Sort and return top_k
        scores.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for sim, doc_id in scores[:top_k]:
            if sim > 0:
                doc = self.documents[doc_id]
                results.append({
                    "id": doc_id,
                    "text": doc["text"],
                    "metadata": doc["metadata"],
                    "score": round(sim, 4)
                })
        return results
