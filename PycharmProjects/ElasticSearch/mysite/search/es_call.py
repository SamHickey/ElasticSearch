from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q, A


# function which searches the elasticsearch index
def esearch(text="", sort_by=""):
    client = Elasticsearch()
    # enter query here, bool allows for multiple fields. Use __ to access and 'dotted fields'
    # can change should to must
    q = Q("match_phrase", text=text)

    # search the medical index for the above query
    # returns first 20 results
    s = Search(using=client, index="medical").query(q).sort(sort_by)
    response = s.execute()
    # use get_results function to dictate what parameters are returned
    search = get_results(response)
    return search


def get_results(response):
    results = []
    for hit in response:
        result_tuple = (hit.text, hit.intents[0].name, hit.intents[0].assessment,
                        hit.dateCreated, hit.intents[0].probability)
        results.append(result_tuple)
    return results

# pass list of intent_name that are being queried
def search_names(names=[]):
    client = Elasticsearch()
    search = []
    # search each term in list
    for name in names:
        q = Q("match_phrase", intents__name=name)
        s = Search(using=client, index='medical').query(q)
        response = s.execute()
        search.append(get_results(response))
    # return a list of results, which in turn is a list
    return search

def search_assessment(assessments=[]):
    client = Elasticsearch()
    search = []
    for assessment in assessments:
        q = Q("match_phrase", intents__assessment=assessment)
        s = Search(using=client, index='medical').query(q)
        response = s.execute()
        search.append(get_results(response))

    return search


# return information on the index such as number of documents and each type of assessment
def index_info():
    client = Elasticsearch()
    q = Q("match", intents__assessment="Correct")
    s = Search(using=client, index="medical").query(q)
    correct = s.execute()
    q = Q("match", intents__assessment="Incorrect")
    s = Search(using=client, index="medical").query(q)
    incorrect = s.execute()
    q = Q("match", intents__assessment="Unknown")
    s = Search(using=client, index="medical").query(q)
    unknown = s.execute()
    results = []
    results_tuple = (len(correct), len(incorrect), len(unknown), len(correct)+len(incorrect)+len(unknown))
    results.append(results_tuple)
    return results

# search for what index names are present in the document
def name_info():
    client = Elasticsearch()
    a = A('terms', field='intents.name.keyword')
    s = Search(using=client, index="medical")

    s.aggs.bucket('names', a)
    s = s.execute()
    results = []
    for name in s.aggregations.names.buckets:
        results.append(name.key)
    return results



