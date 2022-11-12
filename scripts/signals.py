import socket
import time

chat_list = []
package: socket
players_online = 0
nickname = ''
secret_key = ''


def send_chat(msg):
    if len(msg) > 0:
        package.send(('c' + msg).encode())


def update_chat(message):
    words = message.split(' ')
    header = ''  # if other players message
    if '#' in words[0]:  # if announcement or command message
        words[0] = ''
        words.pop(0)
        header = '# '
    elif len(nickname) > 0:  # if current player message
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


def translate(packet):
    global players_online
    if len(packet) > 0:
        header = packet[0]
        content = packet[1:]
        if header == '0':
            update_chat('_')
            # Signal from server. checking if player is still online. Otherwise, server will send user offline
        if header == 'c':  # CHAT
            update_chat(content)
        elif header == 'm':  # MOVE
            print('move character to destined position on the map')
        elif header == 'a':  # ACTION
            print('activate an action or skill which player send request for')
        elif header == 's':  # STATS
            print('update player stats')
        elif header == 'i':  # INVENTORY
            print('update inventory functions')
        elif header == 'l':  # LOOT
            print('display received loot')
        elif header == 'g':  # GUILD
            print('receive guild info')
        elif header == 'd':  # DMG BOX
            print('receive info for dmg box')


def start_spoofing_packets(usr):
    global package
    package = usr
    while True:
        try:
            packet = usr.recv(256).decode()
            translate(packet)
        except socket.error:
            break
    usr.close()


def send_online_status(usr):
    while True:
        time.sleep(3)
        try:
            usr.send('0'.encode())
        except socket.error:
            break
    usr.close()
