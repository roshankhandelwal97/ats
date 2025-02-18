import os
from pinecone import Pinecone, ServerlessSpec

# Load the Pinecone API key from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")
INDEX_NAME = "ats"

# Create an instance of the Pinecone client using the new API.
pc = Pinecone(api_key=PINECONE_API_KEY)

def create_index(dimensions):
    """
    Create the Pinecone index if it doesn't already exist.
    """
    # Get the list of current indexes and extract their names
    existing_indexes = pc.list_indexes().names()
    print(existing_indexes)
    if INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=INDEX_NAME,
            dimension=dimensions,
            metric="cosine",  # or use 'euclidean' as per your use case
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
        )
        print(f"Index '{INDEX_NAME}' created.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")

def upsert_embedding(doc_id, embedding, metadata=None):
    """
    Upsert a vector embedding into the Pinecone index.
    - doc_id: A unique identifier for the document.
    - embedding: The vector embedding (list of floats).
    - metadata: A dictionary with additional info (e.g., {"type": "resume"} or {"type": "jd"}).
    """
    # Obtain the index instance
    index = pc.Index(INDEX_NAME)
    vector = {"id": str(doc_id), "values": embedding, "metadata": metadata or {}}
    index.upsert([vector])


#New Function added by Tanmay to get all the stored id's in pinecone
def get_All_VectorId():

    # Initialize Pinecone
    #Pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

    # Select the Pinecone index where embeddings are stored
    index = pc.Index(INDEX_NAME)
    print("Index "+str(index))

    # Fetch all vector IDs (metadata-only query)
    vector_ids = list(index.list())  # This retrieves all stored IDs

    # Print the vector IDs
    print("Stored Embedding IDs:", vector_ids)

    return vector_ids
