import time

from kivy.clock import Clock
from kivy.utils import platform
if platform == 'android':
    from android.permissions import Permission, request_permissions, check_permission


    def check_permissions(perms):
        for perm in perms:
            if not check_permission(perm):
                return False
        return True


    def ask_for_permission():
        perms = [Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE]

        if not check_permissions(perms):
            request_permissions(perms)  # get android permissions


class AndroidPermissions:
    def __init__(self, start_app=None):
        self.permission_dialog_count = 0
        self.start_app = start_app
        if platform == 'android':
            self.permissions = []
            # self.permissions.append(Permission.WRITE_EXTERNAL_STORAGE)
            # self.permissions.append(Permission.READ_EXTERNAL_STORAGE)
            self.permission_status([], [])
        elif self.start_app:
            self.start_app()

    def permission_status(self, permissions, grants):
        granted = True
        for p in self.permissions:
            granted = granted and check_permission(p)
        if granted:
            if self.start_app:
                self.start_app()
        elif self.permission_dialog_count < 2:
            Clock.schedule_once(self.permission_dialog)

    def permission_dialog(self, dt):
        self.permission_dialog_count += 1
        request_permissions(self.permissions, self.permission_status)
