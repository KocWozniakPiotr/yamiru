import socket
import time
from threading import Thread
from scripts.handlers.player import *

player = PlayerHandler()
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
                self.usr.settimeout(10)
                packet = self.usr.recv(256).decode()
                self.usr.settimeout(None)
            except socket.error as e:
                print(f'[{e}] could not receive packet, breaking loop and usr connection')
                break
            self.translate(packet)
        self.usr.close()

    def translate(self, packet):
        if len(packet) > 0:
            header = packet[0]
            content = packet[1:]
            if header == '0':
                print('-')
                # Signal from server. checking if player is still online. Otherwise, server will send user offline
            if header == 'c':  # CHAT
                pass  # self.update_chat(content)
            elif header == 'm':  # MOVEMENT
                print('move character to destined position on the map')
            elif header == 'a':  # ACTION
                print('activate an action or skill which player send request for')
            elif header == 'p':  # PLAYER
                player.update(packet)
            elif header == 'i':  # INVENTORY
                print('update inventory functions')
            elif header == 'd':  # LOOT
                print('display received drop')
            elif header == 'g':  # GUILD
                print('receive guild info')


class DataSender:
    usr: socket

    def __init__(self, **kwargs):
        self._t_send_online_status = Thread(target=self.send_online_status)

    def activate(self):
        self._t_send_online_status.start()

    def send_online_status(self):
        while True:
            try:
                self.usr.settimeout(10)
                self.usr.send('0'.encode())
                self.usr.settimeout(None)
            except:
                print("awaiting response from server...")
            time.sleep(3)

    def send_nickname(self, profession, skin, nick):
        try:
            self.usr.send((create_character + str(profession) + str(skin) + nick).encode())
        except socket.error:
            pass
