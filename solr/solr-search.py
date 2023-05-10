import gradio as gr
from vector_helper import VectorHelper
import pysolr
import http.client
import json

# Solr configuration
SOLR_ADDRESS = 'http://localhost:8983/solr/Legis'
solr = pysolr.Solr(SOLR_ADDRESS, always_commit=True)

def search_content(query):
    # Convertir el query en vector.
    vh = VectorHelper()
    v = vh.execute(query)
    vector_query = str("{!knn f=vector topK=3}=VECTOR=").replace("=VECTOR=", v)

    conn = http.client.HTTPSConnection("localhost", 8983)
    payload = json.dumps({"query": vector_query})
    headers = {'Content-Type': 'application/json'}
    conn.request("POST", "/solr/Legis/select?fl=id,content,score",
                 payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    # jemplo de resultados
    results = [["Resultado 1", "Resultado 2", "Resultado 3"]]

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
        with gr.Column():
            df = gr.Dataframe(
                headers=["Id", "Texto", "Snipet"],
                datatype=["str", "str", "str"],
                row_count=5,
                col_count=(3, "fixed"),
            )
            btn_search.click(fn=search_content, inputs=txt_criteria,
                             outputs=df, api_name="search_content")

demo.launch()
