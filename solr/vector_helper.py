from sentence_transformers import SentenceTransformer

class VectorHelper:
    def execute(self, sentence):
        # Load or create a SentenceTransformer model

        model = SentenceTransformer('setu4993/LaBSE')
        # Compute sentence embeddings
        embeddings = model.encode([sentence])

        # Create an array of floats comma separated (removing the initial "array" string and the trailing "dtype=float32")
        vector_embeddings = repr(list(embeddings)[0])[6:-22]
        return vector_embeddings
