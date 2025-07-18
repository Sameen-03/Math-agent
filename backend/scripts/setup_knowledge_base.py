import json
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
import os

# --- CONFIGURATION ---
DB_PATH = "../qdrant_db"
COLLECTION_NAME = "math_problems"
DATA_PATH = "../data/math_dataset.json"

# Create the directory for the DB if it doesn't exist
os.makedirs(DB_PATH, exist_ok=True)
print(f"Database will be stored in: {os.path.abspath(DB_PATH)}")

# Initialize the embedding model
print("Loading embedding model...")
encoder = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")

# Initialize Qdrant client to use the local folder
client = QdrantClient(path=DB_PATH)

# Recreate the collection to ensure a fresh start with the new structure
print(f"Creating or recreating collection '{COLLECTION_NAME}'...")
client.recreate_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(
        size=encoder.get_sentence_embedding_dimension(),
        distance=models.Distance.COSINE
    ),
)
print("Collection created.")

# Load data and prepare points for upserting
print("Loading data from JSON file...")
documents = []
try:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        documents = json.load(f)
except json.JSONDecodeError:
    print("Failed to load as single JSON array. Trying JSON Lines format...")
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))

if not documents:
    print("❌ No documents were loaded. Please check the format of math_dataset.json.")
else:
    points_to_upsert = []
    for idx, doc in enumerate(documents):
        # --- THIS IS THE FIX ---
        # We now create a clear 'page_content' field for the retriever to use.
        # We will embed the 'problem' field for searching.
        page_content = f"Problem: {doc.get('problem', '')}\n\nSolution: {doc.get('solution', '')}"
        
        points_to_upsert.append(
            models.PointStruct(
                id=idx,
                vector=encoder.encode(doc["problem"]).tolist(),
                payload={
                    "page_content": page_content
                }
            )
        )

    print(f"Found {len(documents)} documents. Upserting into local Qdrant DB...")
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points_to_upsert,
        wait=True
    )
    print("✅ Local knowledge base setup complete.")