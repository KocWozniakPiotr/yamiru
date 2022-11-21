import time
from kivy.clock import Clock
from kivy.utils import platform


if platform == 'android':
    from android.permissions import Permission, request_permissions, check_permission
    perms = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]

    def check_permissions():
        for perm in perms:
            if not check_permission(perm):
                return False
        return True


    def ask_for_permission():
        if not check_permissions():
            request_permissions(perms)