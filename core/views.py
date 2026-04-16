from django.shortcuts import render

# home (首頁)
def home(request):
    # index.html 
    return render(request, 'index.html')