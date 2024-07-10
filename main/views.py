from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, "main/index.html")

def post_list(request):
    return render(request, "main/post_list.html")