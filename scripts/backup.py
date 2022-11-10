import png
from cryptography.fernet import Fernet
from kivy.core.image import Image
# this fernet key is used only to encrypt client secret locally for backups
f = Fernet(b'iCtOF6HiDXREyjRFhsPws-x3-E6LUsYpESuoHWG0TkA=')

pic_string = []
pic_bump = 8
range_x, range_y = 0, 0


def make_binary(_s):
    global pic_string, range_x, range_y
    noise = 0
    _s = str(_s)
    z = [bin(ord(x))[2:].zfill(8) for x in _s]
    c = ''
    for a in z:
        noise += int(a)
        c += a
        if len(c) == 40:
            pic_string.append(c)
            c = ''
    c = c + (40 - len(c)) * '0'
    pic_string.append(c)
    # distort pic_string wit some kind of noise here


def grow_image(pic, size):
    new_pic = []
    for n in pic:
        for o in range(size):
            new_pic.append(n)
    i = 0
    for r in new_pic:
        old_row = r
        new_row = ''
        for s in old_row:
            new_row += s * size
        new_pic[i] = new_row
        i += 1
    x = 40 * size
    y = len(pic) * size
    return new_pic, x, y


def save_secret_backup(path):
    global pic_string
    pic_string, res_x, res_y = grow_image(pic_string, pic_bump)
    pic_string = [[int(c) for c in row] for row in pic_string]

    w = png.Writer(res_x, res_y, greyscale=True, bitdepth=1, y_pixels_per_unit=32, x_pixels_per_unit=32)
    # file = open('../backup_data.png', 'wb')
    final_dir = path + 'ASYLLION_PROFILE_BACKUP' + '.png'
    file = open(final_dir, 'wb')
    w.write(file, pic_string)
    file.close()
    return final_dir


def clean_secret(_key):
    end_of_string = 0
    temp = ''
    for e in _key:
        temp += e
        if e == "'":
            end_of_string += 1
        if end_of_string == 2:
            break
    return temp


def recover_secret_from_backup(path):
    waiting = True
    r = None
    while waiting:
        try:
            file = open(path + 'ASYLLION_PROFILE_BACKUP.png', 'rb')
            r = png.Reader(file)
            waiting = False
        except:
            waiting = True
    r.read()
    _tup = r.read_flat()
    arr = _tup[2]
    temp_arr = []
    i = 0
    gg = ''
    _width = (pic_bump * 40) - 1
    for g in arr:
        if i < _width:
            gg += str(g)
            i += 1
        else:
            temp_arr.append(gg)
            i = 0
            gg = ''
    ################################################
    _line = 0
    trim_arr = []
    for h in temp_arr:
        if _line % pic_bump == 0:
            trim_arr.append(h)
        _line += 1
    ################################################
    final_arr = ''
    b = 0
    _char = ''
    for x in trim_arr:
        for y in x:
            if b % pic_bump == 0:
                _char += y
            b += 1
        b = 0
        final_arr += _char
        _char = ''
    ################################################
    b = []
    t = ''
    n = 0
    for p in final_arr:
        if n == 8:
            b.append(t)
            t = ''
            n = 0
        t += str(p)
        n += 1
    ################################################
    _key_from_pic = ''.join([chr(int(x, 2)) for x in b])
    print(_key_from_pic)
    print(_key_from_pic[2:142])
    # WTF ?!?!?! DIFFERENT LENGHT OF CHAIN ?!
    final_encrypted = f.decrypt(bytes(clean_secret(_key_from_pic[2:142]).encode()))
    return str(final_encrypted)[1:].replace("'", '')


##########################################################################################################


def do_backup(user_profile, path):
    # this string is pulled from the settings in order to make a local backup
    secret = f.encrypt(bytes(user_profile, encoding='utf8'))
    make_binary(secret)
    return save_secret_backup(path)

# print(recover_secret_from_backup('../'))
