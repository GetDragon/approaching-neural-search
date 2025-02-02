#!/usr/bin/python

from sentence_transformers import SentenceTransformer
import torch
import sys
from itertools import islice
import time

BATCH_SIZE = 100
INFO_UPDATE_FACTOR = 1
MODEL_NAME = 'setu4993/LaBSE' #'all-MiniLM-L6-v2'

# load or create a SentenceTransformer model
model = SentenceTransformer(MODEL_NAME)
# get device like 'cuda'/'cpu' that should be used for computation
if torch.cuda.is_available():
    model = model.to(torch.device("cuda"))
print(model.device)

def main():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    initial_time = time.time()
    batch_encode_to_vectors(input_filename, output_filename)
    finish_time = time.time()
    print('Vectors created in {:f} seconds\n'.format(finish_time - initial_time))

def batch_encode_to_vectors(input_filename, output_filename):
    # open the file containing text
    with open(input_filename, 'r') as documents_file:
        # open the file in which the vectors will be saved
        with open(output_filename, 'w+') as out:
            processed = 0
            # processing 100 documents at a time
            for n_lines in iter(lambda: tuple(islice(documents_file, BATCH_SIZE)), ()):
                processed += 1
                if processed % INFO_UPDATE_FACTOR == 0:
                    print("processed {} batch of documents".format(processed))
                # create sentence embedding
                vectors = encode(n_lines)
                # write each vector into the output file
                for v in vectors:
                    out.write(','.join([str(i) for i in v]))
                    out.write('\n')

def encode(documents):
    embeddings = model.encode(documents, show_progress_bar=True)
    print('vector dimension: ' + str(len(embeddings[0])))
    return embeddings


if __name__ == "__main__":
        main()
