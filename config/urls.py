from django.contrib import admin
from django.urls import path
from core import views  #  app的views.py，裡面有home函式

urlpatterns = [
    path('admin/', admin.site.urls), # 原本的後台urls
    path('', views.home, name='home'), #引號裡空白代表「首頁」
]