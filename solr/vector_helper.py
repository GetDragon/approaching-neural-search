import torch
from sentence_transformers import SentenceTransformer

class VectorHelper:
    def execute(self, sentence):
        # Load or create a SentenceTransformer model

        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        if torch.cuda.is_available():
            model = model.to(torch.device("cuda"))

        # Compute sentence embeddings
        embeddings = model.encode([sentence])

        # Create an array of floats comma separated (removing the initial "array" string and the trailing "dtype=float32")
        vector_embeddings = repr(list(embeddings)[0])[6:-22]
        return vector_embeddings
