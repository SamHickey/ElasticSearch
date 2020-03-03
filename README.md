# elasticsearch
A simple web app to query a document using elasticsearch

elasticsearch/mysite/search/views.py will read data off of the HTML page and send it to the corresponding search function
it also queries the ES document to send information about the document to the HTML page such as number of documents.
so as not to hard-code parameters from the medical document into the web app, views.py will also get information from the document and
then send that to the HTML page. It does this for the intents.name.


elasticsearch/mysite/search/es_call.py uses the elasticsearch_dsl api to query the "medical" document.
Currently there are several different functions to query different parameters of the document ie intents.name, text etc.

elasticsearch/mysite/search/templates/search/index.html contains the html file which is rendered.
