from django.shortcuts import render
from .es_call import *
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
# Create your views here.


def search_index(request):
    text_term = ""
    sort_by = "dateCreated.keyword"  # automatically sorts by date
    assessment = []



    # get sort parameter from sort label
    if request.GET.get('sort'):
        sort_by = request.GET['sort']

    # search intents.name
    intent_names = name_info()
    names = []
    name_term = []
    for name in intent_names:
        i = 0
        name = name.replace(" ", "_")
        names.append(name)
        if request.GET.get(name):
            name_term.append(request.GET[name])
    n = []
    for name in name_term:
        name = name.replace("_", " ")
        n.append(name)
    results = search_names(names=n)

    #search intent.assessment
    if request.GET.get('correct'):
        assessment.append(request.GET['correct'])
    if request.GET.get('incorrect'):
        assessment.append(request.GET['incorrect'])
    if request.GET.get('unknown'):
        assessment.append(request.GET['unknown'])
    test = search_assessment(assessments=assessment)
    for result in test:
        results.append(result)


    # get text parameter from text label on HTML page
    if request.GET.get('text'):
        text_term = request.GET['text']
    search_term = text_term
    # send parameters to elasticSearch function esearch
    text_search = esearch(text=text_term, sort_by=sort_by)
    results.append(text_search)

    # get criteria parameter
    if request.GET.get('criteria'):
        criteria = request.GET['criteria']

    info = index_info()
    context = {'results': results, 'count': len(results), 'info': info,
               'intent_names': intent_names, 'names': names}
    # render HTML page

    return render(request,  'search/index.html',  context)

