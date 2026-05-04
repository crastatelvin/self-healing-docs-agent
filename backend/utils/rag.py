import chromadb
from chromadb.utils import embedding_functions
import os
from typing import List

class RAGManager:
    def __init__(self, db_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Using a simple default embedding function for now
        # In a real 2026 setup, you'd use nomic or gemini embeddings
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="documentation", 
            embedding_function=self.embedding_fn
        )

    def add_documents(self, documents: List[str], metadatas: List[dict], ids: List[str]):
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query_docs(self, query: str, n_results: int = 1):
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        # Return both content and file source
        return [{"content": doc, "source": meta["source"]} for doc, meta in zip(results['documents'][0], results['metadatas'][0])]

if __name__ == "__main__":
    # Test run
    rag = RAGManager()
    rag.add_documents(
        documents=["The calculate_tax function takes amount and rate."],
        metadatas=[{"source": "docs.md"}],
        ids=["doc1"]
    )
    print(rag.query_docs("How does tax calculation work?"))
