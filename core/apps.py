from django.apps import AppConfig
from django.contrib.auth.apps import AuthConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = "局內系統管理"


class CustomAuthConfig(AuthConfig):
    name = 'django.contrib.auth'
    verbose_name = "單一授權管理"
