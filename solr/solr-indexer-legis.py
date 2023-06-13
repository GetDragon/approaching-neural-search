import sys
import pysolr
import time
import json
import os
import re
import copy

from vector_helper import VectorHelper

## Solr configuration
SOLR_ADDRESS = 'http://localhost:8983/solr/Legis'

BATCH_SIZE = 100 # Indexa cada 100 registros
MIN_SENTENCE_LEN = 30
# Create a client instance
solr = pysolr.Solr(SOLR_ADDRESS, always_commit=True)

def split_sentences(text):
    # Lista de caracteres que suelen indicar el final de una oración
    end_punctuations = ['.', '!', '?']

    sentences = []
    current_sentence = ''
    
    for char in text:
        current_sentence += char
        if char in end_punctuations and len(current_sentence) > MIN_SENTENCE_LEN:
            sentences.append(current_sentence.strip())  # Agregar la oración a la lista
            current_sentence = ''

    if current_sentence:
        sentences.append(current_sentence.strip())

    return sentences

def index_documents(documents_filename):
    vh = VectorHelper()
    # open the file containing text
    with open(documents_filename, "r", encoding='utf-8') as documents_file:
        #TODO: repara el archivo para que sea un array de objetos json
        json_string = documents_file.read()
        json_string = json_string.replace('{', '[',1)
        json_string = json_string.replace('"add":{', '')
        json_string = json_string.replace('"doc":{', '{')
        json_string = json_string.replace('}},', '},')
        json_string = json_string.replace('}}}', '}]')

        """new_file = str(documents_filename).replace('.json', '_.json')
        with open(new_file, 'w', encoding='utf-8') as file:
            file.write(json_string)"""
        
        contenido = json.loads(json_string)
        # for each document (text and related vector) creates a JSON document
        index = 0
        documents= []
        for objeto in contenido:
            if len(str(objeto["content"]).strip()) == 0: continue

            objeto["content"] = re.sub(r'\[§\s*(\d+)\]', r'\1 ', objeto["content"])
            sentences = split_sentences(objeto["content"])

            if len(sentences) > 1:
                print("Partiendo párrafo...", len(sentences))
                sentence_count = 0
                for s in sentences:
                    copy_obj = copy.deepcopy(objeto);
                    copy_obj["id"] = f"{copy_obj['id']}_{sentence_count}"
                    copy_obj["content"] = s
                    vectores = vh.execute(s)
                    objeto["vector"] = json.loads(vectores)
                    documents.append(copy_obj) # append JSON document to a list
                    index += 1
                    sentence_count += 1
            else:
                vectores = vh.execute(sentences[0])
                objeto["vector"] = json.loads(vectores)
                documents.append(objeto) # append JSON document to a list
                index += 1

            # to index batches of documents at a time
            if index % BATCH_SIZE == 0 and index != 0:
                # how you'd index data to Solr
                try:
                    solr.add(documents)
                except Exception as e:
                    print(e)
                
                documents = []
                print("==== indexed {} documents ======".format(index))
        # to index the rest, when 'documents' list < BATCH_SIZE
        if documents:
            try:
                solr.add(documents)
            except Exception as e:
                print(e)
            print("==== indexed {} documents ======".format(len(documents)))
        
        print("Finished")
    
    os.rename(documents_filename, str(documents_filename).replace(".json", ".okjson"))

def main():
    initial_time = time.time()
    idcontenido = "regaduanas"
    directorio = f"D:\Data\solr Stuff\{idcontenido}"

    solr.delete(q=f'bookid:{idcontenido}')
    
    for archivo in os.listdir(directorio):
        if archivo.endswith(".json"):
            ruta_archivo = os.path.join(directorio, archivo)
            print(f"Procesando archivo: {ruta_archivo}")
            index_documents(ruta_archivo)

    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))

if __name__ == "__main__":
    main()