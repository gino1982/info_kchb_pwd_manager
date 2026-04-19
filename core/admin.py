import pandas as pd
from django.db import models
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime

from .models import Employee, SystemApp, Account

# 1. 註冊員工表
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'job_title', 'onboard_date', 'is_active')
    list_filter = ('is_active', 'department')
    search_fields = ('name', 'department', 'job_title')

    # ⬇️⬇️⬇️ 新增區塊：擴充 Django 後台網址 ⬇️⬇️⬇️
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-excel/', self.admin_site.admin_view(self.import_excel), name='import_employee_excel'),
        ]
        return my_urls + urls

    # ⬇️⬇️⬇️ 新增區塊：讀取 Excel 的核心邏輯 ⬇️⬇️⬇️
    def import_excel(self, request):
        if request.method == "POST":
            excel_file = request.FILES.get("excel_file")
            
            # 防呆：確認是否有上傳檔案
            if not excel_file:
                messages.error(request, "請選擇一個 Excel 檔案！")
                return redirect("..")
            
            try:
                # 召喚 Pandas 讀取 Excel
                df = pd.read_excel(excel_file)
                count = 0
                
                # 一筆一筆讀取資料並建檔
                for index, row in df.iterrows():
                    # 處理時間格式防呆 (確保 Excel 的時間能被資料庫看懂)
                    onboard_date = pd.to_datetime(row['到職日']).date() if pd.notna(row['到職日']) else datetime.now().date()
                    
                    # update_or_create：如果姓名一樣就更新，沒有就新增 (避免重複建檔)
                    Employee.objects.update_or_create(
                        name=row['姓名'],
                        defaults={
                            'department': row.get('所屬單位', ''),
                            'job_title': row.get('職稱', ''),
                            'onboard_date': onboard_date,
                            'is_active': True
                        }
                    )
                    count += 1
                
                # 成功後顯示你設計的大地色提示訊息！
                messages.success(request, f"太神啦！成功匯入了 {count} 筆員工資料！🎉")
            except Exception as e:
                messages.error(request, f"匯入失敗，請檢查 Excel 格式。錯誤訊息：{str(e)}")
            
            return redirect("..")
        
        # 如果是單純點進網頁，就顯示上傳表單的畫面
        return render(request, "admin/excel_upload.html")
    # ⬆️⬆️⬆️ ------------------------------------ ⬆️⬆️⬆️

# 2. 註冊系統表
@admin.register(SystemApp)
class SystemAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

# 3. 註冊帳密配置表
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('employee', 'system', 'username', 'is_revoked')
    list_filter = ('is_revoked', 'system')
    search_fields = ('employee__name', 'username')