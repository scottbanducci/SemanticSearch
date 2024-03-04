import glob
import os
import numpy as np
from sentence_transformers import SentenceTransformer

model_384tokens = "all-mpnet-base-v2"

def generate_embeddings(text_files_path="./data/text_files", embeddings_path="./data/embeddings", model_name=model_384tokens):
    """
    Generates embeddings for text files and saves them to a specified directory.
    Now skips files that already have an embedding.

    Parameters:
    - text_files_path: str, the path to the directory containing text files.
    - embeddings_path: str, the path to the directory where embeddings will be saved.
    - model_name: str, the name of the model to use for generating embeddings.
    """
    model = SentenceTransformer(f"sentence-transformers/{model_name}")

    # List all .txt files
    text_files = glob.glob(f"{text_files_path}/**/*.txt", recursive=True)

    for file_path in text_files:
        # Construct the new file path for the embedding
        relative_path = os.path.relpath(file_path, text_files_path)
        embedding_file_path = os.path.join(embeddings_path, relative_path).replace('.txt', '.npy')

        # Check if the embedding file already exists
        if os.path.exists(embedding_file_path):
            print(f"Skipping {file_path} as embedding already exists.")
            continue

        # Read the content of the current file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Generate embedding for the content
        embedding = model.encode([content])  # Assuming one document per file, thus [content]

        # Ensure the directory exists for the new embedding file
        new_file_dir = os.path.dirname(embedding_file_path)
        os.makedirs(new_file_dir, exist_ok=True)
        
        # Save the embedding
        np.save(embedding_file_path.replace('.txt', ''), embedding)  # Removes .txt extension and replaces with .npy implicitly by np.save

        print(f"Generated and saved embedding for {file_path}")
