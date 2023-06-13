import gradio as gr
from vector_helper import VectorHelper
import pysolr
import requests
import json

# Solr configuration
SOLR_ADDRESS = "http://localhost:8983/solr/Legis/select?fl=id,content,score"

def search_content(query):
    # Convertir el query en vector.
    vh = VectorHelper()
    v = vh.execute(query)
    payload = json.dumps({
        "query": str("{!knn f=vector topK=25}=VECTOR=").replace("=VECTOR=", v)
    })
    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request("POST", SOLR_ADDRESS, headers=headers, data=payload)

    data = response.json()

    #print(data["response"]["docs"])
    # ejemplo de resultados
    results = []
    for doc in data["response"]["docs"]:
        results.append([doc["id"], doc["content"], doc["score"]])

    return results


with gr.Blocks() as demo:
    gr.Markdown(
        """
    # Busqueda semántica Solr!
    """)
    with gr.Row():
        with gr.Column():
            txt_criteria = gr.Textbox(label="Ingresa el criterio de búsqueda")
            btn_search = gr.Button("Buscar")
    with gr.Row():
        with gr.Column():
            df = gr.Dataframe(
                headers=["Id", "Texto", "Snipet"],
                datatype=["str", "str", "str"],
                row_count=5,
                col_count=(3, "dynamic"),
            )
            btn_search.click(fn=search_content, inputs=txt_criteria,
                             outputs=df, api_name="search_content")

demo.launch()
