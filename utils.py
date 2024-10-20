import os
import pandas as pd
import asyncio
import jwt
import lancedb
import google.generativeai as genai
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import pyarrow as pa

db = None

# Set your Google API key
GOOGLE_API_KEY = "Enter_your_google_API"
genai.configure(api_key=GOOGLE_API_KEY)

# JWT configuration
JWT_SECRET = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30

# ThreadPoolExecutor for CPU-bound tasks
thread_pool = ThreadPoolExecutor(max_workers=os.cpu_count() * 2)

def generate_jwt(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise tornado.web.HTTPError(401, "Token has expired")
    except jwt.InvalidTokenError:
        raise tornado.web.HTTPError(401, "Invalid token")

# Get corresponding db and table
async def get_db_and_table(user_id):
    global db
    if db is None:
        db = await lancedb.connect_async("/tmp/shared_user_db")
    table_name = f"code_chunks_{user_id}"
    return db, table_name

# Google Gemini embeddings
def generate_embeddings(content):
    model = "models/text-embedding-004"
    embedding_response = genai.embed_content(
        model=model,
        content=content,
        output_dimensionality=512
    )
    return embedding_response["embedding"]

# Chunking text
def chunk_code(code, max_bytes=2000):
    lines = code.splitlines()
    chunks = []
    current_chunk = []
    current_bytes = 0
    for line in lines:
        line_bytes = len(line.encode('utf-8'))
        if current_bytes + line_bytes > max_bytes:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_bytes = 0
        current_chunk.append(line)
        current_bytes += line_bytes
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    return chunks

# Get files in folder
def get_all_files_in_folder(folder_path, extension=".py"):
    files = []
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(extension):
                files.append(os.path.join(dirpath, filename))
    return files

# Embedding removal, index and search utilities
async def remove_embeddings_for_folders(folder_paths, db, table_name):
    table = await db.open_table(table_name)
    for folder_path in folder_paths:
        table = await table.delete(f"filename LIKE '{folder_path}%'")
    print(f"Removed embeddings for folders: {folder_paths}")

async def index_code(files, db, table_name):
    embeddings = []
    if table_name in await db.table_names():
        table = await db.open_table(table_name)
        print(f"Table '{table_name}' already exists, opening the table.")
    else:
        schema = pa.schema([
            ('text', pa.string()),
            ('filename', pa.string()),
            ('vector', pa.list_(pa.float32(), 512))  # Assuming 512-dimensional embeddings
        ])
        table = await db.create_table(table_name, schema=schema)
        print(f"Table '{table_name}' did not exist, creating a new table.")

    for file_path in files:
        with open(file_path, 'r') as f:
            code = f.read()
            chunks = chunk_code(code)
            for chunk in chunks:
                embedding_vector = await asyncio.get_event_loop().run_in_executor(
                    thread_pool, generate_embeddings, chunk
                )
                embeddings.append({"text": chunk, "filename": file_path, "vector": embedding_vector})

    if embeddings:
        print(f"Indexing completed for table: {table_name}")
        await table.add(embeddings)
    else:
        print("No embeddings found to index.")

async def search_code(query, db, table_name):
    table = await db.open_table(table_name)
    print(f"Searching for: {query}")
    query_embedding = await asyncio.get_event_loop().run_in_executor(
        thread_pool, generate_embeddings, query
    )
    try:
        results_df = await table.vector_search(query_embedding).limit(5).to_pandas()
        return results_df
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return pd.DataFrame(columns=["filename", "text"]) 