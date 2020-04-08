from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from .es_call import *


def search_index(request):
    # initalise terms
    text_term = ""
    sort_by = "dateCreated.keyword"  # automatically sorts by date
    assessment = []
    start_date = '2000-00-04T00:00'
    end_date = '2020-06-02T13:51'
    index = 'medical'
    range=0

    # get text parameter from text label from page
    if request.GET.get('text'):
        text_term = request.GET['text']
    # get sort parameter from sort label
    if request.GET.get('sort'):
        sort_by = request.GET['sort']
    # get range parameter, this is how many results to display on the page
    if request.GET.get('range'):
        range = int(request.GET['range'])
    # get intent.assessment value(s)
    if request.GET.get('correct'):
        assessment.append(request.GET['correct'])
    if request.GET.get('incorrect'):
        assessment.append(request.GET['incorrect'])
    if request.GET.get('unknown'):
        assessment.append(request.GET['unknown'])
    # Get date range
    if request.GET.get('start'):
        start_date = request.GET['start']
    if request.GET.get('end'):
        end_date = request.GET['end']
    # pass to daterange function to parse to correct format for
    start_date, end_date = daterange(start_date, end_date)

    # get intents.name
    # name_info() will return a list of all intent.names in the index
    intent_names = name_info(index)
    names = []
    name_term = []
    # checkbox values in HTML cannot have spaces so underscores are used instead
    # as a result, must replace each space in each name with an underscore
    for name in intent_names:
        name = name.replace(" ", "_")
        # add the modified name to a new list, which is used to render the HTML page
        names.append(name)
        # request whether that name has been selected from a checkbox
        # add it tp new list name_term
        if request.GET.get(name):
            name_term.append(request.GET[name])

    # in order to query the index, the name terms received from the Web app must be returned to their original value
    # ie replace the underscore with a space
    n = []
    for name in name_term:
        name = name.replace("_", " ")
        n.append(name)

    # get all indexes
    indices = get_indexes()



    # Upload files to index
    if request.method == 'POST' and request.POST.get('index_name'):
        # request file and index name
        uploaded_file = request.FILES['document']
        index_name = request.POST['index_name']
        fs = FileSystemStorage()
        fs.save(uploaded_file.name, uploaded_file)
        index_document(uploaded_file.name, index_name)
        fs.delete(uploaded_file.name)

    # send parameters for search to search function

    search = search_all(assessment, sort_by, names=n, text=text_term, index=index,
                        start_date=start_date, end_date=end_date, range=range)

    # get information on the index to render to the html page
    info = index_info(index)

    # data to be used by HTML page
    context = {'results': search, 'count': len(search), 'info': info, 'names': names, 'indices': indices}
    # render HTML page
    return render(request,  'search/index.html',  context)


def daterange(start, end):
    start_date = start.split('T')[0]
    start_time = start.split('T')[1]
    start_time = start_time + ":00"
    start = start_date + " " + start_time
    end_date = end.split('T')[0]
    end_time = end.split('T')[1]
    end_time = end_time + ":00"
    end = end_date + " " + end_time
    return start, end


