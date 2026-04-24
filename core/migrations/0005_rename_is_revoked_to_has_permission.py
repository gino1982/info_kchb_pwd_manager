# Generated manually: rename is_revoked → has_permission with semantic flip

from django.db import migrations, models


def flip_permission_semantics(apps, schema_editor):
    """RenameField 後欄位仍持有舊語意 (True=無權限)，這裡把每筆值反轉成新語意 (True=有權限)。"""
    Account = apps.get_model('core', 'Account')
    for acc in Account.objects.all():
        acc.has_permission = not acc.has_permission
        acc.save(update_fields=['has_permission'])


def unflip_permission_semantics(apps, schema_editor):
    """反向遷移：把新語意值再翻回舊語意。"""
    Account = apps.get_model('core', 'Account')
    for acc in Account.objects.all():
        acc.has_permission = not acc.has_permission
        acc.save(update_fields=['has_permission'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_account_options_alter_employee_options_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='account',
            old_name='is_revoked',
            new_name='has_permission',
        ),
        migrations.RunPython(flip_permission_semantics, reverse_code=unflip_permission_semantics),
        migrations.AlterField(
            model_name='account',
            name='has_permission',
            field=models.BooleanField(default=True, verbose_name='權限'),
        ),
    ]
