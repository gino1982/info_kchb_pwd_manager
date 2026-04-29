from django.db import models

# 1. 員工表
class Employee(models.Model):
    name = models.CharField(max_length=50, verbose_name="姓名")
    national_id_hash = models.CharField(max_length=64, unique=True, verbose_name="身分證雜湊值")
    national_id_last3 = models.CharField(max_length=3, blank=True, default="", verbose_name="身分證末三碼")
    department = models.CharField(max_length=50, null=True, blank=True, verbose_name="所屬單位")
    job_title = models.CharField(max_length=50, null=True, blank=True, verbose_name="職稱")
    onboard_date = models.DateField(verbose_name="到職日")
    resign_date = models.DateField(null=True, blank=True, verbose_name="離職日")
    is_active = models.BooleanField(default=True, verbose_name="是否在職")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "員工"
        verbose_name_plural = "員工"

# 2. 系統表
class SystemApp(models.Model):
    name = models.CharField(max_length=100, verbose_name="系統名稱")
    url = models.URLField(blank=True, verbose_name="系統網址")
    description = models.TextField(blank=True, verbose_name="備註說明")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "系統"
        verbose_name_plural = "系統"

# 3. 帳密配置表 (核心！)
class Account(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="所屬員工")
    system = models.ForeignKey(SystemApp, on_delete=models.CASCADE, verbose_name="所屬系統")
    username = models.CharField(max_length=100, verbose_name="登入帳號")
    email = models.EmailField(max_length=255, verbose_name="電子信箱")
    has_permission = models.BooleanField(default=True, verbose_name="權限")

    class Meta:
        # 防呆機制：四欄全同才視為重複。
        unique_together = ('employee', 'system', 'username', 'email')
        verbose_name = "帳戶"
        verbose_name_plural = "帳戶"

    def __str__(self):
        return f"{self.employee.name} 的 {self.system.name} 帳號"
