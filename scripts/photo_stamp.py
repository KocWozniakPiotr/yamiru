from datetime import datetime
import png

_ = ['00000',
     '00000',
     '00000',
     '00000',
     '00000']

s = ['11111',
     '10000',
     '11111',
     '00001',
     '11111']

c = ['01111',
     '10000',
     '10000',
     '10000',
     '01111']

i = ['00100',
     '00000',
     '00100',
     '00100',
     '00100']

o = ['01110',
     '10001',
     '10101',
     '10001',
     '01110']

n = ['10001',
     '11001',
     '10101',
     '10011',
     '10001']

f = ['11111',
     '10000',
     '11110',
     '10000',
     '10000']

a = ['01110',
     '10001',
     '11111',
     '10001',
     '10001']

y = ['10001',
     '10001',
     '01110',
     '00100',
     '00100']

l = ['10000',
     '10000',
     '10000',
     '10000',
     '11111']

p = ['11110',
     '10001',
     '11110',
     '10000',
     '10000']

r = ['11110',
     '10001',
     '11110',
     '10010',
     '10001']

e = ['11111',
     '10000',
     '11110',
     '10000',
     '11111']

b = ['11110',
     '10001',
     '11110',
     '10001',
     '11110']

k = ['10001',
     '10010',
     '11000',
     '10010',
     '10001']

u = ['10001',
     '10001',
     '10001',
     '10001',
     '01110']

minus = ['00000',
         '00000',
         '01110',
         '00000',
         '00000']

one = ['00010',
       '00110',
       '01010',
       '00010',
       '00010']

two = ['11111',
       '00001',
       '11111',
       '10000',
       '11111']

three = ['11111',
         '00001',
         '00111',
         '00001',
         '11111']

four = ['10001',
        '10001',
        '11111',
        '00001',
        '00001']

six = ['11111',
       '10000',
       '11111',
       '10001',
       '11111']

seven = ['11111',
         '00001',
         '00010',
         '00100',
         '01000']

eight = ['11111',
         '10001',
         '11111',
         '10001',
         '11111']

nine = ['11111',
        '10001',
        '11111',
        '00001',
        '11111']

letters = [s, c, i, o, n, s, _, o, f, _, a, s, y, l, l, i, o, n]
letters2 = [_, _, p, r, o, f, i, l, e, _, b, a, c, k, u, p, _, _]
letters3 = [_, _, _, _]
numbers = [o, one, two, three, four, s, six, seven, eight, nine, minus]


def grow_image(pic, size):
    new_pic = []
    for _n in pic:
        for _o in range(size):
            new_pic.append(_n)
    _i = 0
    for _r in new_pic:
        old_row = _r
        new_row = ''
        for _s in old_row:
            new_row += _s * size
        new_pic[_i] = new_row
        _i += 1
    return new_pic


def generate_stamp():
    date_label = str(datetime.now())[0:10]
    for _signs in date_label:
        if _signs == '-':
            letters3.append(minus)
        else:
            letters3.append(numbers[int(_signs)])

    letters3.append(_)
    letters3.append(_)
    letters3.append(_)
    letters3.append(_)

    stamp = [letters, letters2, letters3]
    _string = ''
    title = ['1' * 160, '0' * 160, '0' * 160]

    for letter_line in range(3):

        for line in range(5):
            for letter in stamp[letter_line]:
                if len(_string) == 0:
                    _string += '0' * 17
                _string += '00' + letter[line]
            _string += '0' * 17
            title.append(_string)
            _string = ''
        if len(title) < 21:
            title.append('0' * 160)
            title.append('0' * 160)
            title.append('0' * 160)
    return grow_image(title, 2)



'''title = [[int(c) for c in row] for row in title]

w = png.Writer(len(title[0]), len(title), greyscale=True, bitdepth=1)
f = open('png.png', 'wb')
w.write(f, title)
f.close()'''
