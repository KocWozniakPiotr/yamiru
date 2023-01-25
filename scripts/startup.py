import configparser


class ConfigManager:
    user_secret = None
    tutorial = 'empty'
    config = configparser.ConfigParser()
    allow_backup = False
    allow_notify = True
    notify_activated = False

    def active(self):
        # Creates default_settings.ini if not created yet
        try:
            print('trying to read settings')
            open('../settings.ini', 'r')
            print('success!')
            self.config.read('../settings.ini')
            self.tutorial = self.config.get('Startup', 'Tutorial')
            if (self.config.get('Startup', 'Notifications')) == 'on':
                self.allow_notify = True
            else:
                self.allow_notify = False
            if self.tutorial == 'empty' or self.tutorial == 'started':
                return False
            self.tutorial = 'finished'
            return True
        except OSError as e:
            print(f'{e} could not find config so generating a new one')
            new_config = open('../settings.ini', 'a+')
            new_config.write(open("misc/default_settings.ini", 'r').read())
            new_config.close()
            return False

    def start_notification_service(self):
        if not self.notify_activated:
            self.notify_activated = True
            from jnius import autoclass
            service = autoclass('org.kivy.scionsofasyllion.ServiceSyncing')
            mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
            service.start(mActivity, '')
