import socket
from startup import ConfigManager
import ssl
from threading import *
from scripts.signals import *


class ClientConnection:
    usr: socket
    server_connected = False
    wait_for_approval = False
    allow_login_screen = False
    server_status = ''
    progress = 0
    client_version = '111'
    update_available = False
    user_nick = ""
    user_secret = ""

    def server_connect(self):
        time.sleep(1)
        _HOST, _PORT = '0.0.0.0', 5005
        try:
            _HOST = socket.gethostbyname('asyllion.com')
        except socket.error:
            self.server_status += '\n' + 'FAILED! please check your internet connection'
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext()
        try:
            self.usr = context.wrap_socket(sock, server_hostname=_HOST)
        except socket.error:
            self.server_status += '\n' + 'FAILED! please check your internet connection'
            return
        try:
            self.usr.settimeout(5)
            self.usr.connect((_HOST, _PORT))
            self.usr.settimeout(None)
            self.server_status += '\n' + 'connected!'
            self.usr.send('-Cl13NT-G4ME-T0K3N-'.encode())
            self.server_connected = True
            self.server_status += '\n' + 'looking for updates...'
            if self.check_updates():
                if self.send_key():
                    t_spoof_packets = Thread(target=start_spoofing_packets, args=(self.usr,))
                    t_spoof_packets.start()
                    t_send_online_status = Thread(target=send_online_status, args=(self.usr,))
                    t_send_online_status.start()
            elif self.update_available:
                pass

        except socket.error:
            self.server_status += '\n' + 'server maintenance... try again later.'
            self.server_connected = False

    def send_key(self):
        if self.server_connected:
            if not self.wait_for_approval:
                self.wait_for_approval = True
                try:
                    ########################
                    ConfigManager.config.read('../settings.ini')
                    if ConfigManager.config.get('Startup', 'Secret') == 'None':
                        self.server_status += '\n' + 'creating your secret...'
                        # if secret doesn't exist yet, send value 'empty' to receive a new secret
                        self.usr.send('empty'.encode())
                        self.user_secret = self.usr.recv(256).decode()
                        ConfigManager.config.set('Startup', 'Secret', self.user_secret)
                        with open('../settings.ini', 'w') as current_config:
                            ConfigManager.config.write(current_config)
                        self.server_status += '\n' + 'creation successful!'
                        return True
                    else:
                        self.user_secret = ConfigManager.config.get('Startup', 'Secret')
                    ########################

                    self.server_status += '\n' + 'trying to login with your secret...'
                    self.usr.send(self.user_secret.encode())
                    user = self.usr.recv(256).decode()
                    self.wait_for_approval = False
                    if user == 'entering':
                        self.server_status += '\n' + 'greetings!'
                        return True
                    elif user == 'tries':
                        self.server_status += '\n' + 'your secret seems corrupted!'
                        return False
                    elif user == 'soft_ban':
                        self.server_status += '\n' + 'too many failed tries, you got banned for 1 hour!'
                        return False
                    elif user == 'banned':
                        self.server_status += '\n' + '...already banned! You have to wait 1 hour'
                        return False

                except socket.error:
                    self.server_status += '\n' + 'connection failed, try again.'
                    return False
        else:
            self.server_status += '\n' + 'server not responding...'
            return False

    def check_updates(self):
        try:
            latest_version = self.usr.recv().decode()
            if latest_version != self.client_version:
                self.server_status += '\n' + '...new version is available!'
                self.update_available = True
                return False
            else:
                self.server_status += '\n' + 'no new updates found'
            self.client_version = latest_version
            return True
        except socket.error:
            self.server_status += '\n' + '''couldn't retrieve data from server'''
            return False
