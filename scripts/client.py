from scripts.startup import ConfigManager
import ssl
from scripts.signals import *


class ClientConnection:
    host_name = 'sample.com'
    _HOST, _PORT = '0.0.0.0', 5005
    client_version = '111'
    usr: socket
    receiver = DataReceiver()
    sender = DataSender()

    def __init__(self):
        self.server_connected = False
        self.current_status = None
        self.wait_for_approval = False
        self.allow_login_screen = False
        self.progress = 0
        self.update_available = False
        self.user_nick = ""
        self.user_secret = ""
        self.user = ''

    def update_server_message(self):
        if player.server_response != '':
            content = player.server_response
            player.server_response = ''
            return content
        else:
            return ''

    def server_connect(self):
        try:
            self._HOST = socket.gethostbyname(self.host_name)
        except socket.error:
            self.current_status = 'please check your internet connection'
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext()
        try:
            self.usr = context.wrap_socket(sock, server_hostname=self._HOST)
        except socket.error:
            self.current_status = 'please check your internet connection'
            return
        try:
            self.usr.settimeout(5)
            self.usr.connect((self._HOST, self._PORT))
            self.usr.settimeout(None)
            print('connected!')
            self.usr.send('-Cl13NT-G4ME-T0K3N-'.encode())
            self.server_connected = True
            print('looking for updates...')
            if self.check_updates():
                if self.send_key():
                    self.receiver.usr = self.usr
                    self.receiver.activate()
                    self.sender.usr = self.usr
                    self.sender.activate()

            elif self.update_available:
                pass
        except socket.error:
            self.current_status = 'server maintenance... try again later.'
            self.server_connected = False

    def send_key(self):
        if self.server_connected:
            if not self.wait_for_approval:
                self.wait_for_approval = True
                try:
                    ConfigManager.config.read('../settings.ini')
                    if ConfigManager.config.get('Startup', 'Secret') == 'None':
                        print('creating your secret...')
                        # if secret doesn't exist yet, send value 'empty' to receive a new secret
                        self.usr.send('empty'.encode())
                        self.user_secret = self.usr.recv(256).decode()
                        ConfigManager.config.set('Startup', 'Secret', self.user_secret)
                        with open('../settings.ini', 'w') as current_config:
                            ConfigManager.config.write(current_config)
                        print('creation successful!')
                    else:
                        self.user_secret = ConfigManager.config.get('Startup', 'Secret')

                    print('trying to login with your secret...')
                    self.usr.send(self.user_secret.encode())
                    self.user = self.usr.recv(256).decode()
                    print(self.user)
                    self.wait_for_approval = False
                    if self.user == 'entering':
                        print('greetings!')
                        return True
                    elif self.user == 'setup':
                        print('welcome! ...need to finish setup !')
                        return True
                    elif self.user == 'creating':
                        print('welcome new player ^_^')
                        return True
                    elif self.user == 'tries':
                        print('your secret seems corrupted!')
                        return False
                    elif self.user == 'soft_ban':
                        print('too many failed tries, you got banned for 1 hour!')
                        return False
                    elif self.user == 'banned':
                        print('...already banned! You have to wait 1 hour')
                        return False

                except socket.error:
                    print('connection failed, try again.')
                    return False
        else:
            print('server not responding...')
            return False

    def check_updates(self):
        try:
            latest_version = self.usr.recv().decode()
            if latest_version != self.client_version:
                print('...new version is available!')
                self.update_available = True
                return False
            else:
                print('no new updates found')
            self.client_version = latest_version
            return True
        except socket.error:
            print('''couldn't retrieve data from server''')
            return False

    def disconnect_client(self):
        self.usr.shutdown(socket.SHUT_RD)
        self.usr.close()
