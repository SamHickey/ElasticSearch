import json
from pprint import pprint
from django.db import models
from elasticsearch import Elasticsearch

# Create your models here.


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    if _es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return _es


def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search)
    pprint(res)


def text_search():
    es = connect_elasticsearch()
    search_object = {'_source': ['title'], 'query': {'range': {'calories': {'gte': 20}}}}
    search(es, 'medical', json.dumps(search_object))

