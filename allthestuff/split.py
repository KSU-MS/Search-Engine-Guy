import glob
import os
from . import extractText
import json

#path = "/home/nick/Desktop/Projects/Formula-AI/Data/**"

def split_to_json(text, file, json_file, path, chunk_size=200, overlap=50):
    words = text.split()
    step = chunk_size - overlap
    chunks = []

    for i in range(0, len(words), step):
        chunk_words = words[i:i + chunk_size]
        if not chunk_words:
            break

        chunk_text = " ".join(chunk_words)
        chunks.append({
            "chunk_id": len(chunks),
            "start_word": i,
            "end_word": i + len(chunk_words) - 1,
            "text": chunk_text,
            "file": file,
            # "year": year
        })

        if i + chunk_size >= len(words):
            break

    append_to_json(json_file, chunks, path)

def append_to_json(json_file, chunks, path):
    if not os.path.exists(json_file) or os.path.getsize(json_file) == 0:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.extend(chunks)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def main(path):
    path = path + '/**'
    files_and_directories = glob.glob(path, recursive=True)
    files = []
    json_file = "documents.json"
    for entry in files_and_directories:
        if os.path.isfile(entry):
            files.append(entry)

    for file in files:
        text = str(extractText.main(file, "markdown"))
        split_to_json(text, file, json_file, path)

    print("Chunking Completed")