import os
from utils.rag import RAGManager

def ingest_docs(docs_dir):
    rag = RAGManager()
    
    for filename in os.listdir(docs_dir):
        if filename.endswith(".md"):
            file_path = os.path.join(docs_dir, filename)
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Simple chunking by paragraph for now
            paragraphs = content.split('\n\n')
            for i, p in enumerate(paragraphs):
                if len(p.strip()) > 20:
                    rag.add_documents(
                        documents=[p],
                        metadatas=[{"source": filename, "index": i}],
                        ids=[f"{filename}_{i}"]
                    )
    print(f"Ingested documentation from {docs_dir}")

if __name__ == "__main__":
    # Example usage:
    # Create a dummy docs folder and file for testing
    if not os.path.exists("../../docs"):
        os.makedirs("../../docs")
        with open("../../docs/api.md", "w") as f:
            f.write("# API Documentation\n\nThe calculate_tax function takes amount and rate as input.\n\nIt returns the total tax based on a flat 10% rate.")
    
    ingest_docs("../../docs")
