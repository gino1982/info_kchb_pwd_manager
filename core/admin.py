from django.contrib import admin
from django.urls import path

from .excel_import import (
    ImportRowError,
    clean_str,
    get_value,
    handle_excel_import,
    parse_bool,
    parse_date,
    require_str,
    today,
)
from .models import Account, Employee, SystemApp


# 1. 註冊員工表
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'job_title', 'onboard_date', 'is_active')
    list_filter = ('is_active', 'department')
    search_fields = ('name', 'department', 'job_title')

    def get_urls(self):
        my_urls = [
            path(
                'import-excel/',
                self.admin_site.admin_view(self.import_excel),
                name='import_employee_excel',
            ),
        ]
        return my_urls + super().get_urls()

    def import_excel(self, request):
        return handle_excel_import(
            request,
            template_name="admin/excel_upload.html",
            entity_label="員工",
            row_handler=_import_employee_row,
        )


def _import_employee_row(row, row_num):
    name = require_str(get_value(row, ['姓名']), '姓名', row_num)
    onboard_date = parse_date(get_value(row, ['到職日']), default=today)
    Employee.objects.update_or_create(
        name=name,
        defaults={
            'department': clean_str(get_value(row, ['所屬單位'])),
            'job_title': clean_str(get_value(row, ['職稱'])),
            'onboard_date': onboard_date,
            'is_active': True,
        },
    )


# 2. 註冊系統表
@admin.register(SystemApp)
class SystemAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')

    def get_urls(self):
        my_urls = [
            path(
                'import-excel/',
                self.admin_site.admin_view(self.import_excel),
                name='import_system_excel',
            ),
        ]
        return my_urls + super().get_urls()

    def import_excel(self, request):
        return handle_excel_import(
            request,
            template_name="admin/excel_upload_systemapp.html",
            entity_label="系統",
            row_handler=_import_systemapp_row,
        )


def _import_systemapp_row(row, row_num):
    name = require_str(get_value(row, ['系統名稱']), '系統名稱', row_num)
    SystemApp.objects.update_or_create(
        name=name,
        defaults={
            'url': clean_str(get_value(row, ['系統網址'])),
            'description': clean_str(get_value(row, ['備註說明'])),
        },
    )


# 3. 註冊帳密配置表
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('employee', 'system', 'username', 'is_revoked')
    list_filter = ('is_revoked', 'system')
    search_fields = ('employee__name', 'username')

    def get_urls(self):
        my_urls = [
            path(
                'import-excel/',
                self.admin_site.admin_view(self.import_excel),
                name='import_account_excel',
            ),
        ]
        return my_urls + super().get_urls()

    def import_excel(self, request):
        return handle_excel_import(
            request,
            template_name="admin/excel_upload_account.html",
            entity_label="帳戶",
            row_handler=_import_account_row,
        )


def _import_account_row(row, row_num):
    employee_name = require_str(get_value(row, ['員工姓名', '姓名']), '員工姓名', row_num)
    system_name = require_str(get_value(row, ['系統名稱', '所屬系統']), '系統名稱', row_num)
    username = require_str(get_value(row, ['登入帳號', '帳號']), '登入帳號', row_num)
    password = require_str(get_value(row, ['密碼', '加密密碼']), '密碼', row_num)
    is_revoked = parse_bool(get_value(row, ['是否停用', '權限是否已取消']))

    employee = Employee.objects.filter(name=employee_name).first()
    if not employee:
        raise ImportRowError(f"第 {row_num} 列：找不到員工「{employee_name}」")
    system = SystemApp.objects.filter(name=system_name).first()
    if not system:
        raise ImportRowError(f"第 {row_num} 列：找不到系統「{system_name}」")

    Account.objects.update_or_create(
        employee=employee,
        system=system,
        defaults={
            'username': username,
            'password': password,
            'is_revoked': is_revoked,
        },
    )
