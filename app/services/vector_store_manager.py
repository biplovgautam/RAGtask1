'''
Vector DB Interface:
Manages the connection and interaction with your chosen 
Vector Store (Pinecone/Qdrant). It handles the embedding generation and 
the vector storage/retrieval logic used by both the ingestion and RAG services.'''

from typing import List
from app.core.db import pinecone_index, _pc

def embed_and_store_chunks(chunks: List[str], document_id: str):
    """
    Generates embeddings for the given text chunks using Pinecone's Inference API
    and stores them in the Pinecone index.

    Args:
        chunks: A list of text strings to be embedded and stored.
        document_id: The unique ID of the document these chunks belong to.
                     This is used as a namespace or metadata filter.
    """
    if not chunks:
        return

    # Prepare the data for Pinecone
    # We will use the 'multilingual-e5-large' model for embeddings as it is a strong general-purpose model
    # supported by Pinecone's inference API.
    # Note: Ensure your Pinecone index is configured with dimension 1024 for this model.
    
    # Create embedding records
    records = []
    
    # Generate embeddings using Pinecone's Inference API
    # We process in batches to avoid hitting API limits
    batch_size = 96 
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i : i + batch_size]
        
        try:
            # Call Pinecone's Inference API to generate embeddings
            embeddings = _pc.inference.embed(
                model="multilingual-e5-large",
                inputs=batch_chunks,
                parameters={"input_type": "passage", "truncate": "END"}
            )
            
            # Create records for upsert
            for j, embedding_obj in enumerate(embeddings):
                chunk_index = i + j
                chunk_text = batch_chunks[j]
                
                # Create a unique ID for each chunk
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                
                # Prepare metadata
                metadata = {
                    "text": chunk_text,
                    "document_id": document_id,
                    "chunk_index": chunk_index
                }
                
                # Add to records list
                records.append({
                    "id": chunk_id,
                    "values": embedding_obj['values'],
                    "metadata": metadata
                })
                
        except Exception as e:
            print(f"Error generating embeddings for batch {i}: {e}")
            # In a production app, you might want to retry or raise the error
            continue

    # Upsert to Pinecone
    if records:
        try:
            # Store all chunks in the default namespace (no namespace parameter)
            # Chunks are distinguished by document_id in their metadata
            # This allows cross-document search while still being able to filter by document_id
            pinecone_index.upsert(vectors=records)
            print(f"Successfully stored {len(records)} chunks for document {document_id}")
        except Exception as e:
            print(f"Error upserting to Pinecone: {e}")
            raise e


def search_similar_chunks(query: str, top_k: int = 3, document_id: str = None):
    """
    Searches for chunks similar to the query string.
    
    Args:
        query: The user's search query.
        top_k: The number of similar chunks to return.
        document_id: Optional. If provided, filters results to only this document.
        
    Returns:
        A list of matches with text and score.
    """
    try:
        # 1. Generate embedding for the query using Pinecone's Inference API
        query_embedding = _pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[query],
            parameters={"input_type": "query"}
        )
        
        # 2. Search in Pinecone (default namespace, where all documents are stored)
        # If document_id is provided, we can filter by metadata
        query_params = {
            "vector": query_embedding[0]['values'],
            "top_k": top_k,
            "include_metadata": True,
            "include_values": False
        }
        
        # Add metadata filter if document_id is specified
        if document_id:
            query_params["filter"] = {"document_id": {"$eq": document_id}}
        
        results = pinecone_index.query(**query_params)
        
        return results['matches']
        
    except Exception as e:
        print(f"Error searching Pinecone: {e}")
        return []