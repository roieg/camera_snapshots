#!/usr/bin/python3

import requests
from PIL import Image
import io
import os
from datetime import datetime

global debugging

class camera:
    def __init__(self, name, ip):
        self._name = name
        self._ip = ip

    @property
    def ip(self):
        return self._ip

    @property
    def name(self):
        return self._name

def make_dir(path):
    ''' Checks if 'path' exists and if not creates it '''

    if not os.path.exists(path):
        os.mkdir(path)

def pprint(txt):
    ''' If 'debug' is on then prints 'txt' '''

    global debugging
    # Printing the content but making it look slick
    if debugging:
        print('[+]\t{}'.format(txt))

def get_snap(ip):
    ''' Returns a snap from the camera in 'ip' '''

    pprint('trying getting the snapshot from {}'.format(ip))

    # Trying to retrieve the snapshot
    try:
        jpeg = requests.get('http://{}/snap.jpeg'.format(ip), timeout=5)
    except requests.exceptions.Timeout as e:
        pprint('ip did not respond ):')
        return None
    except requests.exceptions.RequestException as e:
        pprint('could not manage to get the snap')
        raise e

    pprint('got the snapshot with status code {}'.format(jpeg.status_code))

    # Checking if we indeed got the snapshot
    if jpeg.status_code == 200:
        jpeg_raw = jpeg.content
        jpeg_image = Image.open(io.BytesIO(jpeg_raw))

        return jpeg_image
    else:
        pprint('oops, something went wrong...')
        return None

def main():
    global debugging
    debugging = False

    root_path = '/mnt/timelaps'

    my_cameras = []

    # Adding the cameras to the list
    my_cameras.append(camera('צלע מערבית', '192.168.1.62'))
    my_cameras.append(camera('בריכה', '192.168.1.98'))
    my_cameras.append(camera('חדר שינה הורים', '192.168.1.97'))
    my_cameras.append(camera('חזית דרומית', '192.168.1.101'))
    my_cameras.append(camera('חזית צפונית', '192.168.1.107'))
    my_cameras.append(camera('חצר אחורית', '192.168.1.103'))
    my_cameras.append(camera('צלע דרומית', '192.168.1.102'))
    my_cameras.append(camera('צלע צפונית', '192.168.1.67'))
    my_cameras.append(camera('רחבת סלון', '192.168.1.100'))
    my_cameras.append(camera('שער כניסה', '192.168.1.99'))
    my_cameras.append(camera('חצר אנגלית', '192.168.1.94'))

    # Going over every camera
    for my_camera in my_cameras:
        # The image that we want to save
        my_jpeg = get_snap(my_camera.ip)

        # The directory to which we shall save the image to
        my_dir = f'{root_path}/{my_camera.name}'
        make_dir(my_dir)

        # The file name with the current date yo
        my_date_on_path = datetime.now().strftime('%y_%m_%d__%H_%M_%S')
        my_file = f'{my_camera.name}_{my_date_on_path}.jpeg'

        # The full path!
        my_path = f'{my_dir}/{my_file}'

        # If we managed to get the file
        if not my_jpeg is None:
            my_jpeg.save(my_path)
            pprint('image saved!')


if __name__ == '__main__':
    main()
