import chromadb
from typing import List, Dict, Any
import json

def initialize_chroma_client() -> chromadb.Client:
    """Initialize and return a ChromaDB client."""
    try:
        return chromadb.Client()
    except Exception as e:
        print(f"Error initializing ChromaDB client: {e}")
        raise

def create_collection(client: chromadb.Client, name: str) -> chromadb.Collection:
    """Create a new collection with the given name."""
    try:
        return client.create_collection(name=name)
    except Exception as e:
        print(f"Error creating collection '{name}': {e}")
        raise

def add_documents(
    collection: chromadb.Collection,
    documents: List[str],
    ids: List[str],
    metadatas: List[Dict[str, Any]] = None
) -> None:
    """Add documents to the collection with optional metadata."""
    try:
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )
        print(f"Successfully added {len(documents)} documents to collection")
    except Exception as e:
        print(f"Error adding documents: {e}")
        raise

def query_collection(
    collection: chromadb.Collection,
    query_texts: List[str],
    n_results: int = 2
) -> Dict[str, Any]:
    """Query the collection and return results."""
    try:
        return collection.query(
            query_texts=query_texts,
            n_results=n_results
        )
    except Exception as e:
        print(f"Error querying collection: {e}")
        raise

def delete_documents(collection: chromadb.Collection, ids: List[str]) -> None:
    """Delete documents from the collection by their IDs."""
    try:
        collection.delete(ids=ids)
        print(f"Successfully deleted documents with IDs: {ids}")
    except Exception as e:
        print(f"Error deleting documents: {e}")
        raise

def get_all_documents(collection: chromadb.Collection) -> Dict[str, Any]:
    """Retrieve all documents from the collection."""
    try:
        return collection.get()
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        raise

def get_documents_by_ids(collection: chromadb.Collection, ids: List[str]) -> Dict[str, Any]:
    """Retrieve specific documents by their IDs."""
    try:
        return collection.get(ids=ids)
    except Exception as e:
        print(f"Error retrieving documents by IDs: {e}")
        raise

def format_results(results: Dict[str, Any]) -> str:
    """Format the results in a structured way."""
    formatted = {
        'ids': results.get('ids', []),
        'distances': results.get('distances', []),
        'metadatas': results.get('metadatas', []),
        'embeddings': results.get('embeddings'),
        'documents': results.get('documents', []),
        'uris': results.get('uris'),
        'data': results.get('data')
    }
    return json.dumps(formatted, indent=2)

def main():
    """Main function to demonstrate ChromaDB usage."""
    try:
        # Initialize client and create collection
        client = initialize_chroma_client()
        collection = create_collection(client, "my_collection")
        
        # Add documents with metadata
        docs = [
            "This document is about New York",
            "This document is about Delhi"
        ]
        ids = ["id3", "id4"]
        metadatas = [
            {"url": "https://en.wikipedia.org/wiki/New_York_City"},
            {"url": "https://en.wikipedia.org/wiki/New_Delhi"}
        ]
        add_documents(collection, docs, ids, metadatas)
        
        # Query collection
        print("\nQuerying for 'Chhole Bhature':")
        results = query_collection(collection, ["Query is about Chhole Bhature"])
        print(format_results(results))
        
    except Exception as e:
        print(f"An error occurred in main: {e}")

if __name__ == "__main__":
    main()