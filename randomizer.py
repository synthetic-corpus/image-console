##############################################
# This gives files a randomized name.        #
# Avoids overwriting before they are loaded. #
# To upload.                                 #
##############################################

import random
import string

def random_name():
    characters = string.ascii_letters + string.digits
    array = [random.choice(characters) for i in range(7)]
    return ''.join(array)

def rename(file_name):
    ext = file_name.split('.')[-1]
    if ext not in ['jpg','png','jpeg']:
        print('not an image file!')
        return None
    else:
        new_name = random_name() + f'.{ext}'
        return new_name

if __name__ == "__main__":
    print('here are some randoms')
    for i in range(4):
        print(random_name())

    print('now with file names')
    files = [
        'flowers.jpeg',
        'flower.png',
        'flour.jpg',
        'follower.bmp'
    ]

    for name in files:
        print(rename(name))