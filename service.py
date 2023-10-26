from datetime import datetime
from plyer import notification
from time import sleep
from jnius import autoclass
import socket
import ssl

# Restarts the service as soon as the script ends.
PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)

# Storing temporary ids of messages in array. They are indexed as templates in a dictionary
msg_storage = []
msg_template = {0: '',
                1: 'amongus is watching you...',
                2: 'hey...',
                3: 'new update available!',
                4: 'you have a new message',
                5: 'L2 lives forever!',
                6: 'your character returned to village',
                7: 'resource farming completed',
                8: 'level up!',
                9: 'please open the game'
                }

# Reads user id form secret for later communication
f = open("../secretkey.mon", 'a+')
f.seek(0)
content = f.read()
if len(content) < 1:
    f.close()
    user_id = ''
    notify = False
else:
    user_id = content[44:]
    notify = True
    f.close()


def server_connected():
    global user_id, msg_storage
    try:
        _HOST = socket.gethostbyname('sample.com')
    except socket.error:
        return False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.SSLContext()
    try:
        usr = context.wrap_socket(sock, server_hostname=_HOST)
    except socket.error:
        return False

    try:
        usr.settimeout(5)
        usr.connect((_HOST, 5005))
        usr.settimeout(None)
        usr.send('your-token'.encode())
        latest_version = usr.recv().decode()
        # add this feature later
        server_version = 111
        if int(latest_version) > server_version:
            print(server_version)
            # login_status = '...new version is available to download!'
        usr.send(str('notify' + user_id).encode())
        msg_storage = [int(m) for m in (usr.recv(256).decode()).split()]
        print(msg_storage)
        return True
    except socket.error:
        return False


# Continuously performs connection to the server and obtains IDs of notifications to display for a user
while True:
    # Adjust sleep depending on duration of your service script
    sleep(300)

    if notify:
        if server_connected():
            for msg_id in msg_storage:
                if msg_id != 0:
                    notification.notify(title=msg_template[msg_id])
            msg_storage.clear()

