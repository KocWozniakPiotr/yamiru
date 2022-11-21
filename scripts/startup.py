import configparser


class ConfigManager:
    user_secret = None
    config = configparser.ConfigParser()
    allow_backup = False

    def active(self):
        # Creates default_settings.ini if not created yet
        try:
            print('trying to read settings')
            open('../settings.ini', 'r')
            print('success!')
            # checking if secret exist
            self.config.read('../settings.ini')
            if self.config.get('Startup', 'Secret') == 'None':
                return False
            return True
        except OSError as e:
            print(f'{e} could not find config so generating a new one')
            new_config = open('../settings.ini', 'a+')
            new_config.write(open("misc/default_settings.ini", 'r').read())
            new_config.close()
            return False


def start_notification_service():
    from jnius import autoclass
    ##################################################################
    service = autoclass('org.kivy.yamiru.ServiceSyncing')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    service.start(mActivity, '')
