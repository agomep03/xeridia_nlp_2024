from sentence_transformers import SentenceTransformer
import faiss

class RAG:

    def __init__(self, embedding_model='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(embedding_model)
        self.index = faiss.IndexFlatL2(384)  
        self.metadata = [] 

    def index_review(self, review, metadata):
        """
        Convierte una reseña en embeddings y guarda el diccionario asociado.
        :param review: Texto de la reseña.
        :param metadata: Diccionario con calificación, canción, artista.
        """
        embedding = self.model.encode([review])
        self.index.add(embedding)
        self.metadata.append(metadata)  

    def retrieve(self, query, top_k=5):
        """
        Recupera los diccionarios asociados a las reseñas más relevantes.
        :param query: Texto de consulta.
        :param top_k: Número de resultados a devolver.
        :return: Lista de diccionarios relevantes.
        """
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, top_k)
        results = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
        return results
