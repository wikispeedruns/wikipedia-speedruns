from abc import ABC, abstractmethod
from wikipedia2vec import Wikipedia2Vec

class EmbeddingsProvider(ABC):
    @abstractmethod
    def get_embedding(self, article: str):
        pass
    
    def get_embeddings(self, articles): 
        return [self.get_embeddings(a) for a in articles]
            
class LocalEmbeddings(EmbeddingsProvider):
    def __init__(self, filename: str):
        self.wiki2vec = Wikipedia2Vec.load_text(filename)

    def get_embedding(self, article: str):
        return self.wiki2vec.get_entity_vector(article)
