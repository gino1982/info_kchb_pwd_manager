from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.urls import path
from django.utils.html import format_html
import hashlib

from .excel_import import (
    ImportRowError,
    clean_str,
    combined_template_response,
    get_value,
    handle_excel_import,
    parse_date,
    parse_permission,
    require_str,
    today,
    upsert,
)
from .models import Account, Employee, SystemApp


_PERMISSION_BADGE = (
    '<span style="display:inline-block;width:18px;height:18px;border-radius:50%;'
    'background:{bg};color:white;text-align:center;line-height:18px;'
    'font-weight:bold;font-size:12px;">{mark}</span>'
)


def _render_permission(has_permission):
    if has_permission:
        return format_html(_PERMISSION_BADGE, bg="#22C55E", mark="✓")
    return format_html(_PERMISSION_BADGE, bg="#EF4444", mark="✗")


def _normalize_national_id(raw_value):
    return clean_str(raw_value).upper()


def _national_id_hash(national_id):
    return hashlib.sha256(national_id.encode("utf-8")).hexdigest()


def _national_id_last3(national_id):
    return national_id[-3:] if len(national_id) >= 3 else national_id


# 1. 註冊員工表
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'national_id_mask', 'department', 'job_title', 'onboard_date', 'active_badge')
    list_filter = ('is_active', 'department')
    search_fields = ('name', 'national_id_last3', 'department', 'job_title')

    @admin.display(description='身分證末三碼', ordering='national_id_last3')
    def national_id_mask(self, obj):
        if not obj.national_id_last3:
            return ""
        return f"***{obj.national_id_last3}"

    @admin.display(description='是否在職', ordering='is_active', boolean=False)
    def active_badge(self, obj):
        return _render_permission(obj.is_active)

    def get_urls(self):
        my_urls = [
            path(
                'import-excel/',
                self.admin_site.admin_view(self.import_excel),
                name='import_employee_excel',
            ),
        ]
        return my_urls + super().get_urls()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def import_excel(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied
        return handle_excel_import(
            request,
            template_name="admin/excel_upload.html",
            entity_label="員工",
            row_handler=_import_employee_row,
        )


def _import_employee_row(row, row_num):
    name = require_str(get_value(row, ['姓名']), '姓名', row_num)
    national_id = require_str(get_value(row, ['身分證號', '身分證字號']), '身分證號', row_num)
    national_id = _normalize_national_id(national_id)
    onboard_date = parse_date(get_value(row, ['到職日']), default=today)
    Employee.objects.update_or_create(
        national_id_hash=_national_id_hash(national_id),
        defaults={
            'name': name,
            'national_id_last3': _national_id_last3(national_id),
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

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def import_excel(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied
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
    list_display = ('employee', 'system', 'email', 'username', 'permission_badge')
    list_filter = ('has_permission', 'system')
    search_fields = ('employee__name', 'username')

    @admin.display(description='權限', ordering='has_permission', boolean=False)
    def permission_badge(self, obj):
        return _render_permission(obj.has_permission)

    def get_urls(self):
        my_urls = [
            path(
                'import-excel/',
                self.admin_site.admin_view(self.import_excel),
                name='import_account_excel',
            ),
            path(
                'import-all/',
                self.admin_site.admin_view(self.import_combined_excel),
                name='import_combined_excel',
            ),
            path(
                'download-template/',
                self.admin_site.admin_view(self.download_combined_template),
                name='download_combined_template',
            ),
        ]
        return my_urls + super().get_urls()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def import_excel(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied
        return handle_excel_import(
            request,
            template_name="admin/excel_upload_account.html",
            entity_label="帳戶",
            row_handler=_import_account_row,
        )

    def import_combined_excel(self, request):
        if not self.has_add_permission(request):
            raise PermissionDenied
        return handle_excel_import(
            request,
            template_name="admin/excel_upload_combined.html",
            entity_label="總表",
            row_handler=_import_combined_row,
        )

    def download_combined_template(self, request):
        return combined_template_response()


def _import_account_row(row, row_num):
    employee_name = require_str(get_value(row, ['員工姓名', '姓名']), '員工姓名', row_num)
    national_id = require_str(get_value(row, ['身分證號', '身分證字號']), '身分證號', row_num)
    national_id = _normalize_national_id(national_id)
    system_name = require_str(get_value(row, ['系統名稱', '所屬系統']), '系統名稱', row_num)
    username = require_str(get_value(row, ['登入帳號', '帳號']), '登入帳號', row_num)
    email = require_str(get_value(row, ['電子信箱', 'Email', 'email']), '電子信箱', row_num)
    has_permission = parse_permission(row)

    employee = Employee.objects.filter(national_id_hash=_national_id_hash(national_id)).first()
    if not employee:
        raise ImportRowError(f"第 {row_num} 列：找不到員工「{employee_name}／***{_national_id_last3(national_id)}」")
    system = SystemApp.objects.filter(name=system_name).first()
    if not system:
        raise ImportRowError(f"第 {row_num} 列：找不到系統「{system_name}」")

    Account.objects.update_or_create(
        employee=employee,
        system=system,
        username=username,
        email=email,
        defaults={
            'has_permission': has_permission,
        },
    )


def _import_combined_row(row, row_num):
    """總表匯入：一列同時建立/更新員工、系統、帳號。"""
    employee_name = require_str(get_value(row, ['員工姓名', '姓名']), '員工姓名', row_num)
    national_id = require_str(get_value(row, ['身分證號', '身分證字號']), '身分證號', row_num)
    national_id = _normalize_national_id(national_id)
    system_name = require_str(get_value(row, ['系統名稱', '所屬系統']), '系統名稱', row_num)
    username = require_str(get_value(row, ['登入帳號', '帳號']), '登入帳號', row_num)
    email = require_str(get_value(row, ['電子信箱', 'Email', 'email']), '電子信箱', row_num)

    employee = upsert(
        Employee,
        lookup={'national_id_hash': _national_id_hash(national_id)},
        values={
            'name': employee_name,
            'national_id_last3': _national_id_last3(national_id),
            'department': clean_str(get_value(row, ['所屬單位'])),
            'job_title': clean_str(get_value(row, ['職稱'])),
            'onboard_date': parse_date(get_value(row, ['到職日']), default=None),
        },
        create_defaults={'onboard_date': today(), 'is_active': True},
    )

    system = upsert(
        SystemApp,
        lookup={'name': system_name},
        values={
            'url': clean_str(get_value(row, ['系統網址'])),
            'description': clean_str(get_value(row, ['備註說明'])),
        },
    )

    Account.objects.update_or_create(
        employee=employee,
        system=system,
        username=username,
        email=email,
        defaults={
            'has_permission': parse_permission(row),
        },
    )
