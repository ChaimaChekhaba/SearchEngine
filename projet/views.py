# importing required packages
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt

from utils.TrecAnalyser import *
from utils.Evaluation import *
from projet.forms import IRForm


# disabling csrf (cross site request forgery)
@csrf_exempt
def index(request):
    # if post request came
    # read_queries("Short")
    # read_queries("Long")

    if request.method == 'POST':
        # getting values from post
        form = IRForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            data = request.POST.copy()

            query = data.get('query')
            cleaning = data.getlist('cleaning')
            similarity = data.getlist('similarity')
            improve = data.getlist('improve')
            imp = int(improve[0])
            launch_lucene()
            documents = search(query, choose_analyser(cleaning), int(similarity[0]),
                               imp)
            # getting our show data template
            template = loader.get_template('index.html')
            return HttpResponse(template.render({"documents": documents, "form": form}, request))

    else:
        # if post request is not true
        template = loader.get_template('index.html')
        form = IRForm()

    # return HttpResponse(template.render({'form': form}))
    return render(request, 'index.html', {'form': form})


def choose_analyser(cleaning):
    if ['0'] == cleaning:  # WhiteSpaceAnalyser
        return 0

    if ['1'] == cleaning:  # StandardAnalyzer removing stop words
        return 1

    if ['2'] == cleaning:  # PorterStemmerAnalyzer
        return 2

    if ['3'] == cleaning:  # KrovetzStemmerAnalyzer
        return 3

    if ['4'] == cleaning:  # LemmatizerAnalyzer
        return 4

    if ['5'] == cleaning:
        return 5


