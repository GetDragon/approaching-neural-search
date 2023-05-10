import sys
import pysolr
import time
import json
import os

from vector_helper import VectorHelper

## Solr configuration
SOLR_ADDRESS = 'http://localhost:8983/solr/Legis'

BATCH_SIZE = 100 # Indexa cada 100 registros
# Create a client instance
solr = pysolr.Solr(SOLR_ADDRESS, always_commit=True)

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
            vectores = vh.execute(objeto["content"])
            objeto["vector"] = json.loads(vectores)
            #print(objeto)
            # append JSON document to a list
            documents.append(objeto)
            index += 1

            # to index batches of documents at a time
            if index % BATCH_SIZE == 0 and index != 0:
                # how you'd index data to Solr
                solr.add(documents)
                documents = []
                print("==== indexed {} documents ======".format(index))
        # to index the rest, when 'documents' list < BATCH_SIZE
        if documents:
            solr.add(documents)
            print("==== indexed {} documents ======".format(len(documents)))
        
        print("Finished")
    
    os.rename(documents_filename, str(documents_filename).replace(".json", ".okjson"))

def main():
    initial_time = time.time()
    directorio = "D:\Data\solr Stuff\solr-json"

    solr.delete(q='*:*')
    
    for archivo in os.listdir(directorio):
        if archivo.endswith(".json"):
            ruta_archivo = os.path.join(directorio, archivo)
            print(f"Procesando archivo: {ruta_archivo}")
            index_documents(ruta_archivo)

    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))

if __name__ == "__main__":
    main()