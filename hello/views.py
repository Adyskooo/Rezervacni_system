from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
   data = {
       "title": "Moje první django stránka",
       "test": list(range(10)),
       "test2": {
           "foo": "bar"
           }
       }
   return render(request, "hello/index.html", data)