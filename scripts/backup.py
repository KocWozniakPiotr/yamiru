from cryptography.fernet import Fernet
import png
from scripts.photo_stamp import generate_stamp

# this fernet key is used only to encrypt client secret locally for backups
f = Fernet(b'iCtOF6HiDXREyjRFhsPws-x3-E6LUsYpESuoHWG0TkA=')
file_dir = '/Pictures/ASYLLION_BACKUP.png'
pic_string = []
pic_bump = 8
range_x, range_y = 0, 0


def make_binary(_s):
    global pic_string, range_x, range_y
    pic_string = []
    _s = str(_s)
    z = [bin(ord(x))[2:].zfill(8) for x in _s]
    c = ''
    for a in z:
        c += a
        if len(c) == 40:
            pic_string.append(c)
            c = ''
    c = c + (40 - len(c)) * '0'
    pic_string.append(c)
    # pic_string.reverse()
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
    for b in new_pic:
        print(b)
    # added generated stamp and added additional height to the secret pic
    _stamp = generate_stamp()
    _stamp_y = len(_stamp)
    # original secret pic 272 px + stamp = 320 when using 9 letters prefix for user ID, example : ID= xxxxxx365
    new_pic += _stamp
    x = 40 * size
    y = (len(pic) * size) + _stamp_y
    return new_pic, x, y


def save_secret_backup(path):
    global pic_string
    pic_string, res_x, res_y = grow_image(pic_string, pic_bump)
    pic_string = [[int(c) for c in row] for row in pic_string]

    w = png.Writer(res_x, res_y, greyscale=True, bitdepth=1, y_pixels_per_unit=32, x_pixels_per_unit=32)
    file = open(path, 'wb')
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


def recover_secret_from_backup(path):
    r = None
    try:
        file = open(path, 'rb')
        r = png.Reader(file)
    except:
        return 'failed'
    r.read()
    _tup = r.read_flat()
    arr = _tup[2]
    temp_arr = []
    i = 0
    gg = ''
    _width = (pic_bump * 40) - 1

    # values from array are being appended each time when i hits _width value. Trimming stamp is not obligatory !
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
    print(_key_from_pic[2:170])
    # WTF ?!?!?! DIFFERENT LENGTH OF CHAIN ?! ...yeah depending on how long is the user  id
    final_encrypted = f.decrypt(bytes(clean_secret(_key_from_pic[2:170]).encode()))
    user_secret = str(final_encrypted)[1:].replace("'", '')
    return user_secret[:44] + user_secret[44:].replace('x', '')


##########################################################################################################
def search_backups():
    try:
        from jnius import autoclass
    except:
        pass
    _environment = autoclass('android.os.Environment')
    sdcard_path = _environment.getExternalStorageDirectory().getAbsolutePath()

    try:
        file = open(sdcard_path + file_dir, 'r')
        file.close()
        return 'exist'
    except:
        return 'empty'


def restore_from_backup():
    from jnius import autoclass
    _environment = autoclass('android.os.Environment')
    sdcard_path = _environment.getExternalStorageDirectory().getAbsolutePath()

    return recover_secret_from_backup(sdcard_path + file_dir)


def backup_data(user_secret):
    from jnius import autoclass, cast
    environment = autoclass('android.os.Environment')
    sdcard_path = environment.getExternalStorageDirectory().getAbsolutePath()

    user_id = user_secret[44:]
    while len(user_id) < 9:
        user_id += 'x'

    secret = f.encrypt(bytes(user_secret[:44]+user_id, encoding='utf8'))
    make_binary(secret)
    save_secret_backup(sdcard_path + file_dir)

    #  creates activity for rescanning photo gallery
    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    activity = PythonActivity.mActivity
    currentActivity = cast('android.app.Activity', activity)
    File = autoclass('java.io.File')
    Uri = autoclass('android.net.Uri')
    Intent = autoclass('android.content.Intent')
    Context = cast('android.content.Context', currentActivity.getApplicationContext())

    # schedule media scan inside gallery to generate thumbnail for photo file
    file = Uri.fromFile(File(sdcard_path + file_dir))
    mediaScanIntent = Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE, file)
    Context.sendBroadcast(mediaScanIntent)

