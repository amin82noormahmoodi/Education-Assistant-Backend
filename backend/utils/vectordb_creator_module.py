import json
from langchain_community.vectorstores import FAISS

class DummyEmbeddings:
    def embed_query(self, text):
        raise NotImplementedError
    def embed_documents(self, texts):
        raise NotImplementedError

def create_faiss_vectordb(json_path, faiss_path):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    chunks = [item["chunk"] for item in data]
    embeddings = [item["embedding"] for item in data]
    vectorstore = FAISS.from_embeddings(
        text_embeddings = list(zip(chunks, embeddings)),
        embedding = DummyEmbeddings(),
        metadatas = [{"id":i} for i in range(len(chunks))]
    )
    try:
        vectorstore.save_local(faiss_path)
    except Exception as e:
        print(f"Error saving FAISS vectorstore: {e}")