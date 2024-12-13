# sentence_transformer_wrapper.py
from sentence_transformers import SentenceTransformer
from sklearn.base import BaseEstimator, TransformerMixin

class SentenceTransformerWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.embedder = SentenceTransformer(model_name)

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return self.embedder.encode(X, show_progress_bar=False)
