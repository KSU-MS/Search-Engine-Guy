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

def main():
    app = Flask(__name__, static_folder='static')
    CORS(app)

    class SemanticSearchEngine:
        def __init__(self, embeddings_file='search_index_embeddings.npy', 
                     chunks_file='search_index_chunks.json',
                     model_name='all-MiniLM-L6-v2'):
            """Initialize the search engine"""
            print("Loading model...")
            self.model = SentenceTransformer(model_name)
            
            print("Loading embeddings...")
            self.embeddings = np.load(embeddings_file)
            
            print("Loading chunks...")
            with open(chunks_file, 'r', encoding='utf-8') as f:
                self.chunks = json.load(f)
            
            print(f"Loaded {len(self.chunks)} chunks with {self.embeddings.shape[1]}-dimensional embeddings")
        
        def extract_filters(self, query: str) -> tuple[str, str, str]:
            cleaned_query = query
            ks_filter = None
            subfolder_filter = None
            
            ks_pattern = r'\bks\s*(\d+)\b'
            ks_match = re.search(ks_pattern, query, re.IGNORECASE)
            if ks_match:
                ks_number = ks_match.group(1)
                ks_filter = f"ks{ks_number}"
                cleaned_query = re.sub(ks_pattern, '', cleaned_query, flags=re.IGNORECASE).strip()
            
            folder_pattern = r'\b(?:folder|subfolder):\s*([^\s]+)'
            folder_match = re.search(folder_pattern, query, re.IGNORECASE)
            if folder_match:
                subfolder_filter = folder_match.group(1)
                cleaned_query = re.sub(folder_pattern, '', cleaned_query, flags=re.IGNORECASE).strip()
            
            return cleaned_query, ks_filter, subfolder_filter
        
        def search(self, query: str, top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
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
                    if isinstance(chunk, dict):
                        file_field = chunk.get('file', '')
                        if ks_filter and ks_filter.lower() not in file_field.lower():
                            continue
                        if subfolder_filter and subfolder_filter.lower() not in file_field.lower():
                            continue
                    else:
                        if ks_filter or subfolder_filter:
                            continue
                    
                    results.append({'score': score, 'chunk': chunk})
            
            return results

    # Initialize search engine
    print("Initializing search engine...")
    search_engine = SemanticSearchEngine()

    # --- Flask routes ---
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    @app.route('/api/search', methods=['POST'])
    def search_route():
        try:
            data = request.json
            query = data.get('query', '')
            top_k = data.get('top_k', 6)
            threshold = data.get('threshold', 0.3)
            if not query:
                return jsonify({'error': 'Query is required'}), 400
            results = search_engine.search(query, top_k=top_k, threshold=threshold)
            return jsonify({'success': True, 'results': results, 'count': len(results)})
        except Exception as e:
            print(f"Error during search: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate_summary', methods=['POST'])
    def generate_summary_route():
        try:
            data = request.json
            query = data.get('query', '')
            results = data.get('results', [])
            model = data.get('model', 'summaryModelMedium:latest')
            if not query or not results:
                return jsonify({'error': 'Query and results are required'}), 400
            
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
                yield f"data: {json.dumps({'type': 'status', 'message': fun_message})}\n\n"
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
    def health_route():
        return jsonify({
            'status': 'ok',
            'chunks_loaded': len(search_engine.chunks),
            'embedding_dim': search_engine.embeddings.shape[1]
        })

    @app.route('/api/subfolders', methods=['GET'])
    def get_subfolders_route():
        try:
            subfolders = set()
            for chunk in search_engine.chunks:
                if isinstance(chunk, dict):
                    file_path = chunk.get('file', '')
                    if file_path:
                        parts = file_path.replace('\\', '/').split('/')
                        for i in range(len(parts) - 1):
                            folder = parts[i]
                            if folder:
                                subfolders.add(folder)
            return jsonify({'success': True, 'subfolders': sorted(list(subfolders)), 'count': len(subfolders)})
        except Exception as e:
            print(f"Error getting subfolders: {e}")
            return jsonify({'error': str(e)}), 500

    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    print("\n" + "="*50)
    print("Server starting on http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)


# --- entry point for uv ---
if __name__ == "__main__":
    main()
