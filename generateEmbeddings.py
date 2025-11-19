from sentence_transformers import SentenceTransformer
import json
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
document_JSON = "documents.json"

def load_Chunks (document_JSON):
    with open(document_JSON, 'r', encoding='utf-8') as docs:
        data = json.load(docs)
    return data

def generate_Embeddings(chunks, model_name='all-MiniLM-L6-v2', batch_size=32):
    """
    Generate embeddings for all chunks in 'documents.json'
    
    Arguments:
        chunks: List of dicts with 'text' field, or list of strings
        model_name: Sentence transformer model to use
        batch_size: Number of chunks to process at once (this is set to run on my laptop rn, but
        eventually we'll have better hardware)
    """
    print(f"Loading model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Extract text from chunks
    if isinstance(chunks[0], dict):
        texts = [chunk['text'] for chunk in chunks]
    else:
        texts = chunks
    
    print(f"Generating embeddings for {len(texts)} chunks...")
    # encode with progress bar
    embeddings = model.encode(
        texts, 
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    return embeddings

# def generate_Embeddings(chunks, model = 'all-MiniLM-L6-v2', batch_Size = 16):
#     print(f"loading {model}...")
#     loaded_Model = SentenceTransformer(model)

#     print("generating embeddings...")
#     if isinstance(chunks[0], dict):
#         texts = [chunk['text'] for chunk in chunks]
#     else:
#         texts = chunks

#     embeddings = model.encode(
#         texts, 
#         batch_Size=batch_Size,
#         show_progress_bar=True,
#         convert_to_numpy=True
#     )

#     return embeddings

def save_Embeddings(chunks, embeddings, output_prefix='search_index'):
    np.save(f'{output_prefix}_embeddings.npy', embeddings)

    with open(f'{output_prefix}_chunks.json', 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    print(f"Saved embeddings to {output_prefix}_embeddings.npy")
    print(f"Saved chunks to {output_prefix}_chunks.json")


def main():
    chunks = load_Chunks(document_JSON)

    print(f"{len(chunks)} chunks loaded")

    embeddings = generate_Embeddings(chunks)

    save_Embeddings(chunks, embeddings)

    print("Done! :)")

