from django.contrib import admin
from django.urls import path
from core import views  #  app的views.py，裡面有home函式

admin.site.site_header = '高雄市政府衛生局_系統帳密管理'  # 左上角的「logo」
admin.site.site_title = '衛生局帳密系統'                 # 瀏覽器標籤的title
admin.site.index_title = '後台管理首頁'                  # 後台首頁的標題

urlpatterns = [
    path('admin/', admin.site.urls), # 原本的後台urls
    path('', views.home, name='home'), #引號裡空白代表「首頁」
    path('api/dashboard/', views.dashboard_api, name='dashboard_api'), # 新增：圖表專用的數據 API
]

