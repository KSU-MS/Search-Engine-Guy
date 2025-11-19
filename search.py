import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import ollama
from ollama import chat


class SemanticSearchEngine:
    def __init__(self, embeddings_file='search_index_embeddings.npy', 
                 chunks_file='search_index_chunks.json',
                 model_name='all-MiniLM-L6-v2'):
        """
        Initialize the search engine
        
        Args:
            embeddings_file: Path to .npy file with embeddings
            chunks_file: Path to JSON file with chunk metadata
            model_name: Same model used to generate embeddings
        """
        print("Loading model...")
        self.model = SentenceTransformer(model_name)
        
        print("Loading embeddings...")
        self.embeddings = np.load(embeddings_file)
        
        print("Loading chunks...")
        with open(chunks_file, 'r', encoding='utf-8') as f:
            self.chunks = json.load(f)
        
        print(f"Loaded {len(self.chunks)} chunks with {self.embeddings.shape[1]}-dimensional embeddings")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search for most relevant chunks
        
        Args:
            query: Search query string
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
        
        Returns:
            List of dicts with chunk data and similarity scores
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Compute cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= threshold:
                result = {
                    'score': score,
                    'chunk': self.chunks[idx]
                }
                results.append(result)
        
        return results
    
    def print_results(self, results: List[Dict[str, Any]], show_full_text: bool = True):
        """Pretty print search results"""
        if not results:
            print("No results found.")
            return
        
        print(f"\nFound {len(results)} results:\n")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            score = result['score']
            chunk = result['chunk']
            
            print(f"\n{i}. Similarity: {score:.4f}")
            
            # Print metadata
            if isinstance(chunk, dict):
                for key, value in chunk.items():
                    if key == 'text':
                        continue
                    print(f"   {key}: {value}")
                
                # Print text
                text = chunk.get('text', str(chunk))
            else:
                text = chunk
            
            if show_full_text:
                print(f"\n   Text: {text}")
            else:
                # Show first 200 characters
                preview = text[:200] + "..." if len(text) > 200 else text
                print(f"\n   Text: {preview}")
            
            print("-" * 80)

def main():
    """Interactive search interface"""
    engine = SemanticSearchEngine()
    
    print("\n" + "=" * 10)
    print("Ask Away:")
    print("=" * 10)
    print("\nCommands:")
    print("  - Type your query and press Enter to search")
    print("  - Type 'quit' or 'exit' to quit")
    print("  - Type 'config' to adjust settings")
    
    top_k = 6
    threshold = 0.3
    show_full_text = True
    
    while True:
        query = input("\nEnter search query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if query.lower() == 'config':
            print(f"\nCurrent settings:")
            print(f"  top_k = {top_k}")
            print(f"  threshold = {threshold}")
            print(f"  show_full_text = {show_full_text}")
            
            try:
                new_k = input(f"\nNumber of results ({top_k}): ").strip()
                if new_k:
                    top_k = int(new_k)
                
                new_threshold = input(f"Minimum similarity ({threshold}): ").strip()
                if new_threshold:
                    threshold = float(new_threshold)
                
                new_show = input(f"Show full text? (y/n, currently {'y' if show_full_text else 'n'}): ").strip().lower()
                if new_show:
                    show_full_text = new_show == 'y'
                
                print("\nSettings updated!")
            except ValueError as e:
                print(f"Invalid input: {e}")
            continue
        
        if not query:
            continue
        
        # Perform search
        results = engine.search(query, top_k=top_k, threshold=threshold)
        engine.print_results(results, show_full_text=show_full_text)

        stream = chat(
            model='summaryModelFormula',
            messages=[{'role': 'user', 'content': f"Query: {query}, Document: {results}"}],
            stream=True,
        )

        for chunk in stream:
            print(chunk['message']['content'], end='', flush=True)

# def ui_Search(query):
#     engine = SemanticSearchEngine()

#     top_k = 5
#     threshold = 0.0
#     show_full_text = True
    
#     query = query.strip()

#     # Perform search
#     results = engine.search(query, top_k=top_k, threshold=threshold)
#     return results

main()