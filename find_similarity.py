import numpy as np
import glob
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model_384tokens = "all-mpnet-base-v2"

model = SentenceTransformer(f"sentence-transformers/{model_384tokens}")
embeddings_path = "./data/embeddings"

def find_similar_embeddings(query, top_n=5):
    """
    Convert a query string to an embedding and find the most similar embedding files.
    
    :param query: A string for which to find the most similar document embeddings.
    :param top_n: Number of top similar files to return.
    :return: A sorted list of tuples (file_path, similarity_score), with the most similar files first.
    """
    query_embedding = model.encode([query])[0]  # Get the embedding for the query
    similarity_scores = []

    # Iterate over all .npy files in the embeddings directory
    for embedding_file in glob.glob(os.path.join(embeddings_path, '**/*.npy'), recursive=True):
        # Load the embedding
        doc_embedding = np.load(embedding_file)
        doc_embedding_squeezed = doc_embedding.squeeze()
        
        # Compute the cosine similarity
        similarity = cosine_similarity([query_embedding], [doc_embedding_squeezed])[0][0]
        
        # Append the similarity and file path to the list
        similarity_scores.append((embedding_file, similarity))

    # Sort the list by similarity score in descending order
    similarity_scores.sort(key=lambda x: x[1], reverse=True)

    # Return the top_n most similar files and their scores
    return similarity_scores[:top_n]