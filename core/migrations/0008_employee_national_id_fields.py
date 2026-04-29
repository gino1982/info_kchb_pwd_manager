from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_account_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='national_id_hash',
            field=models.CharField(default='', max_length=64, unique=True, verbose_name='身分證雜湊值'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='employee',
            name='national_id_last3',
            field=models.CharField(blank=True, default='', max_length=3, verbose_name='身分證末三碼'),
        ),
    ]
