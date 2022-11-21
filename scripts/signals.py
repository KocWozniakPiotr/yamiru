import socket
import time
from threading import Thread

from scripts.handlers.player import PlayerDict

chat_list = []
nickname = ''


class DataReceiver:
    usr: socket
    packet = ''

    def __init__(self, **kwargs):
        self._t_start_spoofing_packets = Thread(target=self.start_spoofing_packets)

    def activate(self):
        self._t_start_spoofing_packets.start()

    def start_spoofing_packets(self):
        while True:
            try:
                self.translate(self.usr.recv(256).decode())
            except socket.error:
                break
        self.usr.close()

    def translate(self, packet):
        if len(packet) > 0:
            header = packet[0]
            content = packet[1:]
            if header == '0':
                pass
                # Signal from server. checking if player is still online. Otherwise, server will send user offline
            if header == 'c':  # CHAT
                self.update_chat(content)
            elif header == 'm':  # MOVEMENT
                print('move character to destined position on the map')
            elif header == 'a':  # ACTION
                print('activate an action or skill which player send request for')
            elif header == 'p':  # PLAYER
                print('update player stats')
            elif header == 'i':  # INVENTORY
                print('update inventory functions')
            elif header == 'd':  # LOOT
                print('display received drop')
            elif header == 'g':  # GUILD
                print('receive guild info')

    def update_chat(self, message):
        words = message.split(' ')
        # if other players message
        header = ''
        # if announcement or command message
        if '#' in words[0]:
            words[0] = ''
            words.pop(0)
            header = '# '
            # if current player message
        elif len(nickname) > 0:
            if nickname in words[0]:
                header = ' '
        temp_line = header
        for x in words:
            if len(x + temp_line) + 2 < 50:
                temp_line += x + '  '
            else:
                chat_list.insert(0, temp_line)
                temp_line = header + x + '  '
        if len(temp_line) < 50:
            chat_list.insert(0, temp_line)
        while len(chat_list) > 100:
            chat_list.pop()


class DataSender:
    usr: socket

    def __init__(self, **kwargs):
        self._t_send_online_status = Thread(target=self.send_online_status)

    def activate(self):
        self._t_send_online_status.start()

    def send_online_status(self):
        while True:
            time.sleep(3)
            try:
                self.usr.send('0'.encode())
            except socket.error:
                break
        self.usr.close()

    def send_nickname(self, nick):
        try:
            self.usr.send((PlayerDict.nick_change + nick).encode())
        except socket.error:
            return

    def send_chat(self, msg):
        if len(msg) > 0:
            self.usr.send(('c' + msg).encode())
