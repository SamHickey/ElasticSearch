from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q, A
import jsonlines

client = Elasticsearch()


# search all criteria
def search_all(assessments, sort_by, names, text, index, start_date, end_date, range):
    should = []
    must = []
    # for each assessment term selected, create a query to that term
    # each assessment term is appended to the must list
    for assessment in assessments:
        must.append(Q("match", intents__assessment=assessment))
    # do the same for the name terms if
    for name in names:
        must.append(Q("match_phrase", intents__name=name))
    # create a query for all these terms, setting the list equal to should.
    # this is to ensure in the final query one of the parameters is returned, and not all
    must = Q("bool", should=must)
    # create a query for the text
    if text != "":
        should = (Q("match_phrase", text=text))

    # use 'bool' to search multiple queries
    # should is used to return any document which matches any query
    q = Q("bool", must=must, should=should, minimum_should_match=1)
    s = Search(using=client, index=index).query(q).sort(sort_by) \
            .filter('range', **{'dateCreated.keyword': {"gte": start_date, "lte": end_date}})[0:range]
    response = s.execute()
    results = get_results(response)
    return results


def get_results(response):
    results = []
    for hit in response:
        result_tuple = (hit.text, hit.intents[0].name, hit.intents[0].assessment,
                        hit.dateCreated, hit.intents[0].probability)
        results.append(result_tuple)
    return results


# return information on the index such as number of documents and each type of assessment
def index_info(index):
    q = Q("match", intents__assessment="Correct")
    s = Search(using=client, index=index).query(q)
    correct = s.execute()
    q = Q("match", intents__assessment="Incorrect")
    s = Search(using=client, index=index).query(q)
    incorrect = s.execute()
    q = Q("match", intents__assessment="Unknown")
    s = Search(using=client, index=index).query(q)
    unknown = s.execute()
    results = []
    results_tuple = (len(correct), len(incorrect), len(unknown), len(correct) + len(incorrect) + len(unknown))
    results.append(results_tuple)
    return results


# search for what index names are present in the document
def name_info(index):
    a = A('terms', field='intents.name.keyword')
    s = Search(using=client, index=index)
    s.aggs.bucket('names', a)
    s = s.execute()
    results = []
    for name in s.aggregations.names.buckets:
        results.append(name.key)
    return results

# upload a document to an index or create a new one
def index_document(uploaded_file, index_name):
    create_index(index_name)
    # for each line, add to document
    def gendata():
        with jsonlines.open(uploaded_file, mode='r') as reader:
            for line in reader:
                yield {
                    "_index": index_name,
                    "_type": "_doc",
                    "_source": line,
                }
    # use bulk api to index document
    helpers.bulk(client, gendata())



def create_index(index_name):
    # create mapping for the index
    mapping = {
        "mappings": {
            "properties": {
                "dateCreated": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "id": {"type": "text",
                       "index": "false"},
                "intents": {
                    "properties": {
                        "assessment": {"type": "keyword"},
                        "name": {"type": "text",
                                 "index_prefixes": {},
                                 "fields": {
                                     "keyword": {
                                         "type": "keyword",
                                         "ignore_above": 256
                                     }
                                 }
                                 },
                        "probability": {"type": "long"}
                    }
                },
                "text": {"type": "text"},
                "version": {
                    "properties": {
                        "domain": {
                            "properties": {
                                "id": {"type": "text",
                                       "index": "false"
                                       }
                            }
                        },
                        "id": {"type": "text",
                               "index": "false"
                               }
                    }
                }
            }
        }
    }
    # create index
    response = client.indices.create(
        index=index_name,
        body=mapping,
        ignore=400  # ignore 400 already exists code
    )

    # catch API error response
    if 'error' in response:
        print("ERROR:", response['error']['root_cause'])
        print("TYPE:", response['error']['type'])


# get all indexes in Elasticsearch
def get_indexes():
    indices = []
    # make a list of the default indexes created by elasticsearch
    default_indices = [".apm-agent-configuration", ".kibana_1", ".kibana_2", ".kibana_task_manager_1", ".tasks", "metricbeat-7.5.2"]
    # find what indices are in Elasticsearch and add any not in the default one to a list
    for index in client.indices.get('*'):
        if index not in default_indices:
            indices.append(index)
    return indices

