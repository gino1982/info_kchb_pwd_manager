from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


GROUPS = {
    '檢視人員': [
        'view_employee',
        'view_systemapp',
        'view_account',
    ],
    '帳密管理員': [
        'view_employee',
        'view_systemapp',
        'view_account', 'add_account', 'change_account',
    ],
    '資料維護員': [
        'view_employee', 'add_employee', 'change_employee',
        'view_systemapp', 'add_systemapp', 'change_systemapp',
        'view_account', 'add_account', 'change_account',
    ],
}


class Command(BaseCommand):
    help = '建立預設的使用者群組與權限（三種角色：檢視人員、帳密管理員、資料維護員）'

    def handle(self, *args, **options):
        for group_name, codenames in GROUPS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            perms = []
            for codename in codenames:
                try:
                    perms.append(Permission.objects.get(codename=codename))
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  找不到權限：{codename}'))
            group.permissions.set(perms)
            action = '建立' if created else '更新'
            self.stdout.write(f'  {action} 群組：{group_name}（{len(perms)} 項權限）')

        self.stdout.write(self.style.SUCCESS('群組設定完成！超管可至「使用者」頁面，為帳號指派群組。'))
