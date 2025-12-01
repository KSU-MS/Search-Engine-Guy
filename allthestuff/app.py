from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import re
import os
from ollama import chat
import random
import _pickle

def main():
    app = Flask(__name__, static_folder='static')
    CORS(app)

    class SemanticSearchEngine:
        def __init__(self, embeddings_file='search_index_embeddings.npy', 
                     chunks_file='search_index_chunks.json',
                     model_name='Qwen/Qwen3-Embedding-0.6B'):
            """Initialize the search engine"""
            print("Loading model...")
            self.model = SentenceTransformer(model_name)
            
            print("Loading embeddings...")
            try:
                # Try loading as regular numpy array first
                self.embeddings = np.load(embeddings_file)
            except (ValueError, _pickle.UnpicklingError) as e:
                print(f"Standard load failed: {e}")
                print("Attempting to fix corrupted file...")
                # File might have corrupt bytes at the start - try to fix it
                with open(embeddings_file, 'rb') as f:
                    data = f.read()
                
                # Check if it starts with UTF-8 BOM or replacement character
                if data[:3] == b'\xef\xbf\xbd':
                    print("Found corrupt bytes at start, removing them...")
                    # Skip the corrupt bytes and save to a temp file
                    fixed_file = embeddings_file + '.fixed'
                    with open(fixed_file, 'wb') as f:
                        f.write(data[3:])  # Skip first 3 bytes
                    
                    # Try loading the fixed file with allow_pickle
                    self.embeddings = np.load(fixed_file, allow_pickle=True)
                    print("Successfully loaded fixed embeddings!")
                else:
                    # Try with allow_pickle on original file
                    self.embeddings = np.load(embeddings_file, allow_pickle=True)
            
            print("Loading chunks...")
            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            print(f"Loaded {len(self.chunks)} chunks with {self.embeddings.shape[1]}-dimensional embeddings")
            print(f"Model produces {self.model.get_sentence_embedding_dimension()}-dimensional embeddings")
            
            # Verify dimensions match
            if self.embeddings.shape[1] != self.model.get_sentence_embedding_dimension():
                raise ValueError(
                    f"Embedding dimension mismatch! "
                    f"Loaded embeddings have {self.embeddings.shape[1]} dimensions, "
                    f"but model '{model_name}' produces {self.model.get_sentence_embedding_dimension()} dimensions. "
                    f"Please use the same model that created the embeddings."
                )
        
        def extract_filters(self, query: str) -> tuple[str, str, str]:
            """
            Extract KS and subfolder filters from query if present
            
            Args:
                query: Search query string
            
            Returns:
                Tuple of (cleaned_query, ks_filter, subfolder_filter)
            """
            cleaned_query = query
            ks_filter = None
            subfolder_filter = None
            
            # Match "ks" followed by optional space and digits (case insensitive)
            ks_pattern = r'\bks\s*(\d+)\b'
            ks_match = re.search(ks_pattern, query, re.IGNORECASE)
            
            if ks_match:
                ks_number = ks_match.group(1)
                ks_filter = f"ks{ks_number}"
                cleaned_query = re.sub(ks_pattern, '', cleaned_query, flags=re.IGNORECASE).strip()
            
            # Match "folder:" or "subfolder:" followed by text (case insensitive)
            folder_pattern = r'\b(?:folder|subfolder):\s*([^\s]+)'
            folder_match = re.search(folder_pattern, query, re.IGNORECASE)
            
            if folder_match:
                subfolder_filter = folder_match.group(1)
                cleaned_query = re.sub(folder_pattern, '', cleaned_query, flags=re.IGNORECASE).strip()
            
            return cleaned_query, ks_filter, subfolder_filter
        
        def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
            """Search for most relevant chunks"""
            cleaned_query, ks_filter, subfolder_filter = self.extract_filters(query)
            
            if ks_filter:
                print(f"Filtering results for: {ks_filter}")
            if subfolder_filter:
                print(f"Filtering results for subfolder: {subfolder_filter}")
            
            query_embedding = self.model.encode([cleaned_query])[0]
            
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                score = float(similarities[idx])
                if score >= threshold:
                    chunk = self.chunks[idx]
                    
                    # Apply filters if present
                    if isinstance(chunk, dict):
                        file_field = chunk.get('file', '')
                        
                        # Apply KS filter
                        if ks_filter and ks_filter.lower() not in file_field.lower():
                            continue
                        
                        # Apply subfolder filter
                        if subfolder_filter and subfolder_filter.lower() not in file_field.lower():
                            continue
                    else:
                        if ks_filter or subfolder_filter:
                            continue
                    
                    result = {
                        'score': score,
                        'chunk': chunk
                    }
                    results.append(result)
            
            return results

    # Initialize search engine
    print("Initializing search engine...")
    search_engine = SemanticSearchEngine()

    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return send_from_directory('static', 'index.html')

    @app.route('/api/search', methods=['POST'])
    def search_route():
        """Search endpoint"""
        try:
            data = request.json
            query = data.get('query', '')
            top_k = data.get('top_k', 6)
            threshold = data.get('threshold', 0.3)
            
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            
            results = search_engine.search(query, top_k=top_k, threshold=threshold)
            
            return jsonify({
                'success': True,
                'results': results,
                'count': len(results)
            })
        
        except Exception as e:
            print(f"Error during search: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate_summary', methods=['POST'])
    def generate_summary():
        """Generate AI summary from search results using streaming"""
        try:
            data = request.json
            query = data.get('query', '')
            results = data.get('results', [])
            model = data.get('model', 'summaryModelMedium:latest')
            
            if not query or not results:
                return jsonify({'error': 'Query and results are required'}), 400
            
            # Random fun messages
            messages = [
                "Consulting the orb...",
                "Asking the gods...",
                "Contacting John for an answer...",
                "Fucking around and finding out...",
                "Counting gizmos...",
                "Dropping the ACC...",
                "Freezing the stapler...",
                "Welding AIRs together...",
                "Puncturing LiPos...",
                "Playing jenga with stock aluminum..."
            ]
            
            fun_message = random.choice(messages)
            
            def generate():
                # Send the fun message first
                yield f"data: {json.dumps({'type': 'status', 'message': fun_message})}\n\n"
                
                # Stream the AI response
                try:
                    stream = chat(
                        model=model,
                        messages=[{'role': 'user', 'content': f"Query: {query}, Document: {results}"}],
                        stream=True,
                    )
                    
                    for chunk in stream:
                        content = chunk['message']['content']
                        yield f"data: {json.dumps({'type': 'content', 'text': content})}\n\n"
                    
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    
                except Exception as e:
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        
        except Exception as e:
            print(f"Error during summary generation: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'chunks_loaded': len(search_engine.chunks),
            'embedding_dim': search_engine.embeddings.shape[1]
        })

    @app.route('/api/subfolders', methods=['GET'])
    def get_subfolders():
        """Get list of unique subfolders from chunks"""
        try:
            subfolders = set()
            
            for chunk in search_engine.chunks:
                if isinstance(chunk, dict):
                    file_path = chunk.get('file', '')
                    if file_path:
                        # Extract folder names from path
                        # Handle both forward and backslashes
                        parts = file_path.replace('\\', '/').split('/')
                        
                        # Add each folder part (excluding the filename)
                        for i in range(len(parts) - 1):
                            folder = parts[i]
                            if folder:  # Skip empty strings
                                subfolders.add(folder)
            
            # Sort subfolders alphabetically
            sorted_subfolders = sorted(list(subfolders))
            
            return jsonify({
                'success': True,
                'subfolders': sorted_subfolders,
                'count': len(sorted_subfolders)
            })
        
        except Exception as e:
            print(f"Error getting subfolders: {e}")
            return jsonify({'error': str(e)}), 500

    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*50)
    print("Server starting on http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()