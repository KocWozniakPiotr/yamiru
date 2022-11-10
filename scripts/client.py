import socket
import startup
import ssl
from threading import *
from scripts.signals import *

usr: socket
server_connected = False
wait_for_approval = False
allow_login_screen = False
_status = 'Welcome to Asyllion'
progress = 0
client_version = '001'
update_available = False
user_nick = ""
user_secret = ""


def server_connect():
    global _status, server_connected, usr
    time.sleep(1)
    _HOST, _PORT = '0.0.0.0', 5005
    try:
        _HOST = socket.gethostbyname('asyllion.com')
    except socket.error:
        _status = 'FAILED! please check your internet connection'
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.SSLContext()
    try:
        usr = context.wrap_socket(sock, server_hostname=_HOST)
    except socket.error:
        _status = 'FAILED! please check your internet connection'
        return
    try:
        usr.settimeout(5)
        usr.connect((_HOST, _PORT))
        usr.settimeout(None)
        _status = 'connected!'
        usr.send('-Cl13NT-G4ME-T0K3N-'.encode())
        server_connected = True
        _status = 'looking for updates...'
        if check_updates():
            if send_key():
                t_spoof_packets = Thread(target=start_spoofing_packets, args=(usr,))
                t_spoof_packets.start()
                t_send_online_status = Thread(target=send_online_status, args=(usr,))
                t_send_online_status.start()
        elif update_available:
            pass

    except socket.error:
        _status = 'server maintenance... try again later.'
        server_connected = False


t_server_connect = Thread(target=server_connect)


def send_key():
    global wait_for_approval, _status, user_secret
    if server_connected:
        if not wait_for_approval:
            wait_for_approval = True
            try:
                ########################
                startup.config.read('../settings.ini')
                if startup.config.get('Startup', 'Secret') == 'None':
                    _status = 'creating your secret...'
                    # if secret doesn't exist yet, send value 'empty' to receive a new secret
                    usr.send('empty'.encode())
                    user_secret = usr.recv(256).decode()
                    startup.config.set('Startup', 'Secret', user_secret)
                    with open('../settings.ini', 'w') as current_config:
                        startup.config.write(current_config)
                    _status = 'creation successful!'
                    return True
                else:
                    user_secret = startup.config.get('Startup', 'Secret')
                ########################

                _status = 'trying to login with your secret...'
                usr.send(user_secret.encode())
                user = usr.recv(256).decode()
                wait_for_approval = False
                if user == 'entering':
                    # login_status = 'greetings!'
                    return True
                elif user == 'tries':
                    _status = 'your secret seems corrupted!'
                    return False
                elif user == 'soft_ban':
                    _status = 'too many failed tries, you got banned for 1 hour!'
                    return False
                elif user == 'banned':
                    _status = '...already banned! You have to wait 1 hour'
                    return False

            except socket.error:
                _status = 'connection failed, try again.'
                return False
    else:
        _status = 'server not responding...'
        return False


def check_updates():
    global _status, client_version, update_available
    try:
        latest_version = usr.recv().decode()
        if latest_version != client_version:
            print(client_version)
            _status = '...new version is available!'
            update_available = True
            return False
        else:
            _status = 'no new updates found'
        client_version = latest_version
        return True
    except socket.error:
        _status = '''couldn't retrieve data from server'''
        return False
