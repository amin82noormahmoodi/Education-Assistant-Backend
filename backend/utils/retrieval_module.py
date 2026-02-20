from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS


class DummyEmbeddings:
    def embed_query(self, text):
        raise NotImplementedError

    def embed_documents(self, texts):
        raise NotImplementedError


class FaissRetriever:
    def __init__(self, faiss_path: str, model_path: str):
        self.faiss_path = faiss_path
        self.model = SentenceTransformer(model_path)
        self.vectorstore = FAISS.load_local(
            faiss_path,
            embeddings=DummyEmbeddings(),
            allow_dangerous_deserialization=True
        )

    def _embed_query(self, query: str):
        return self.model.encode(query).tolist()

    def search(self, query: str, top_k: int = 5):
        query_embedding = self._embed_query(query)

        docs = self.vectorstore.similarity_search_by_vector(
            query_embedding,
            k=top_k)

        return [doc.page_content for doc in docs]