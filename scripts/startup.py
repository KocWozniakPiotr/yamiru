import configparser


class ConfigManager:
    user_secret = None
    tutorial = 'empty'
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
            self.tutorial = self.config.get('Startup', 'Tutorial')
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


def start_notification_service():
    from jnius import autoclass
    ##################################################################
    service = autoclass('org.kivy.yamiru.ServiceSyncing')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    service.start(mActivity, '')
