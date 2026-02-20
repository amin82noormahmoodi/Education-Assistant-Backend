from sentence_transformers import SentenceTransformer

def embed_chunk(chunk):
    model = SentenceTransformer("embedding_model")
    return model.encode(chunk)