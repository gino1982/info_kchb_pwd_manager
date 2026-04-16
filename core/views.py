# feature/real-diverge 分支的修改
from django.shortcuts import render

# home (首頁)
def home(request):
    # index.html 
    return render(request, 'index.html')