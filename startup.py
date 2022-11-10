import configparser
from scripts import backup
from scripts import android_permissions

config = configparser.ConfigParser()
user_secret = None


def start_notification_service():
    from jnius import autoclass
    ##################################################################
    service = autoclass('org.kivy.yamiru.ServiceSyncing')
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    service.start(mActivity, '')


def backup_data():
    from jnius import autoclass, cast
    environment = autoclass('android.os.Environment')
    sdcard_path = environment.getExternalStorageDirectory().getAbsolutePath()
    file_to_scan_path = backup.do_backup("PnA_i1Qfb2oY4XxHvkK2QcB2xnFMqjoY0UoXMI4EtY8=4", sdcard_path + '/Pictures/')

    #  creates activity for rescanning photo gallery
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    currentActivity = cast('android.app.Activity', activity)
    File = autoclass('java.io.File')
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    Context = cast('android.content.Context', currentActivity.getApplicationContext())

    # schedule media scan inside gallery to generate thumbnail for photo file
    file = Uri.fromFile(File(file_to_scan_path))
    mediaScanIntent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, file)
    Context.sendBroadcast(mediaScanIntent)


def restore_backup():
    global user_secret
    from jnius import autoclass
    _environment = autoclass('android.os.Environment')
    sdcard_path = _environment.getExternalStorageDirectory().getAbsolutePath()

    android_permissions.ask_for_permission()
    user_secret = backup.recover_secret_from_backup(sdcard_path + '/Pictures/')
    if user_secret is not None:
        config.read('../settings.ini')
        config.set('Startup', 'Secret', user_secret)
        with open('../settings.ini', 'w') as current_config:
            config.write(current_config)
        # client.t_server_connect.start()
    else:
        # backup failed
        pass


def config_active():
    # Creates default_settings.ini if not created yet
    try:
        print('trying to read settings')
        open('../settings.ini', 'r')
        print('success!')
        # checking if secret exist
        config.read('../settings.ini')
        if config.get('Startup', 'Secret') == 'None':
            return False
        return True
    except OSError as e:
        print(f'{e} could not find config so generating a new one')
        create_config()
        return False


def create_config():
    new_config = open("../settings.ini", 'a+')
    new_config.write(open("default_settings.ini", 'r').read())
    new_config.close()

# webbrowser.open('https://asyllion.com')
