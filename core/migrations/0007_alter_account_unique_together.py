from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_remove_account_password_account_email'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='account',
            unique_together={('employee', 'system', 'username', 'email')},
        ),
    ]
