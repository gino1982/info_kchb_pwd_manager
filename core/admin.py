from django.db import models
from django.contrib import admin
from .models import Employee, SystemApp, Account

# 1. 註冊員工表，並設定在列表頁顯示哪些欄位
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'job_title', 'onboard_date', 'is_active') # 列表顯示的欄位
    list_filter = ('is_active', 'department')# 右側增加「是否在職」的過濾器
    search_fields = ('name', 'department', 'job_title')    # 姓名/單位/職稱 搜尋框

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