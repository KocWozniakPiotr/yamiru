import socket
import ssl
import time
from threading import *
from random import random as r

from scripts.signals import *

usr: socket
usr_wrapped = False
server_connected = False
wait_for_approval = False
allow_login_screen = False
login_status = 'connecting to server...'
progress = 0
server_version = 111
user_nick = ""
user_secret = ""


def read_user_profile():
    global user_secret
    f = open("../secretkey.mon", 'a+')
    f.seek(0)
    content = f.read()
    if len(content) < 1:
        # if secret doesn't exist yet, send value 'empty' to receive a new secret
        usr.send('empty'.encode())
        user_secret = usr.recv(256).decode()
        # user_nick = "anon" + str(int(r() * 999999999))
        f.write(user_secret)
    else:
        user_secret = content
    f.close()


def server_connect():
    global login_status, server_connected, usr, usr_wrapped
    time.sleep(1)
    _HOST, _PORT = '0.0.0.0', 5005
    try:
        _HOST = socket.gethostbyname('asyllion.com')
    except socket.error:
        login_status = 'FAILED! please check your internet connection'
        return
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.SSLContext()
    try:
        usr = context.wrap_socket(sock, server_hostname=_HOST)
        usr_wrapped = True
    except socket.error:
        login_status = 'FAILED! please check your internet connection'
        return
    try:
        usr.settimeout(5)
        usr.connect((_HOST, _PORT))
        usr.settimeout(None)
        login_status = 'connected!'
        usr.send('-Cl13NT-G4ME-T0K3N-'.encode())
        server_connected = True
        login_status = 'looking for updates...'
        check_updates()
        read_user_profile()
        if send_pass(user_secret):
            t_spoof_packets = Thread(target=start_spoofing_packets, args=(usr,))
            t_spoof_packets.start()
            t_send_online_status = Thread(target=send_online_status, args=(usr,))
            t_send_online_status.start()
    except socket.error:
        login_status = 'server maintenance... try again later.'
        server_connected = False


t_server_connect = Thread(target=server_connect)


def send_pass(secret):
    global wait_for_approval, login_status
    if server_connected:
        if not wait_for_approval:
            wait_for_approval = True
            credentials = secret
            try:
                usr.send(credentials.encode())
                user = usr.recv(256).decode()
                wait_for_approval = False
                if user == 'entering':
                    login_status = 'greetings!'
                    return True
                elif user == 'tries':
                    login_status = 'incorrect credentials.'
                    return False
                elif user == 'soft_ban':
                    login_status = 'too many failed tries, you got banned for 1 hour!'
                    return False
                elif user == 'banned':
                    login_status = '...already banned! You have to wait 1 hour'
                    return False
                elif user == 'in-game':
                    login_status = 'the account already logged in, wait few seconds for log out'
                    return False
            except socket.error:
                login_status = 'connection failed, try again.'
                return False
    else:
        login_status = 'server not responding...'
        return False


def check_updates():
    global login_status, server_version
    try:
        latest_version = usr.recv().decode()
        if int(latest_version) > server_version:
            print(server_version)
            login_status = '...new version is available!'
        else:
            login_status = 'no new updates found'
        server_version = int(latest_version)
        time.sleep(1)
        login_status = 'trying to login with your secret'
    except socket.error:
        login_status = '''couldn't retrieve data from server'''
