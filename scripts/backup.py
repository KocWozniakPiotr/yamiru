from datetime import datetime
import png
from cryptography.fernet import Fernet

# This will be generated on the server side !
key = Fernet.generate_key()
f = Fernet(key)
d = bytes(str(datetime.now()), encoding='utf8')
secret = f.encrypt(d)

pic_string = []
pic_bump = 8
range_x, range_y = 0, 0
_values = [1, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1]


def encrypt_backup(noise):
    global pic_string
    noisy_arr = []
    _char = ''
    i = 0
    for x in pic_string:
        for y in x:
            if i > 8:
                i = 0
            if _values[int(noise[i])*2] != 0:
                _char += str(_values[int(noise[i])])
            else:
                _char += str(y)
            i += 1
        noisy_arr.append(_char)
        _char = ''
    pic_string = noisy_arr


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
    encrypt_backup(str(noise))


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


def save_secret_backup():
    global pic_string
    pic_string, res_x, res_y = grow_image(pic_string, pic_bump)
    pic_string = [[int(c) for c in row] for row in pic_string]

    w = png.Writer(res_x, res_y, greyscale=True, bitdepth=1, y_pixels_per_unit=32, x_pixels_per_unit=32)
    file = open('../backup_data.png', 'wb')
    w.write(file, pic_string)
    file.close()


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


def recover_secret_from_backup():
    r = png.Reader('../backup_data.png')
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
    print(clean_secret(_key_from_pic))


# make_binary(secret)
# save_secret_backup()
# recover_secret_from_backup()
