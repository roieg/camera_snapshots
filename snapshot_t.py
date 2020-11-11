#!/usr/bin/python3

import requests
from PIL import Image
import io
import os
from datetime import datetime

DEBUGGING = False

ROOT_PATH =     '/home/pi/timelaps'
DATE_FORMAT =   '%y_%m_%d__%H_%M_%S' 
CAMERAS_FILE =  '/home/pi/cameras' 

IP_INDEX = 0
NAME_INDEX = 1
SEPERATOR = ':'

class Camera:
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
    """
    Checks if 'path' exists and if not creates it

    :param path:    The path we want to make sure exists
    :type path:     str
    """

    if not os.path.exists(path):
        os.mkdir(path)


def pprint(txt):
    """
    If 'debug' is on then prints 'txt'

    :param txt:     The text we want to print
    :type txt:      str
    """

    global DEBUGGING
    # Printing the content but making it look slick
    if DEBUGGING:
        print('[+]\t{}'.format(txt))


def get_snap(ip):
    """
    Returns a snap from the camera in 'ip'

    :param ip:      The ip in which the camera is found
    :type ip:       str
    """

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


def snap_cameras(cam_list):
    """
    Snapping every camera on the list

    :param cam_list:    The list of cameras we want to snap
    :type cam_list:     list
    """

    make_dir(ROOT_PATH)
    for camera in cam_list:
        # The image that we want to save
        my_jpeg = get_snap(camera.ip)

        # The directory to which we shall save the image to
        my_dir = os.path.join(ROOT_PATH, camera.name)
        make_dir(my_dir)

        # The file name with the current date yo
        my_date_on_path = datetime.now().strftime(DATE_FORMAT)
        my_file = f'{camera.name}_{my_date_on_path}.jpeg'

        # The full path!
        my_path = os.path.join(my_dir, my_file)

        # If we managed to get the file
        if not my_jpeg is None:
            my_jpeg.save(my_path)

   
def ret_cameras():
    """
    Retrieves all the cameras from CAMERAS_FILE
    """
    with open(CAMERAS_FILE, 'r') as f:
        lines = f.readlines()

    tup_lis = [(line.split(SEPERATOR)[IP_INDEX].strip(), line.split(SEPERATOR)[NAME_INDEX].strip()) for line in lines]
    cam_list = [Camera(item[NAME_INDEX], item[IP_INDEX]) for item in tup_lis]
    
    return cam_list


def main():
    my_cameras = ret_cameras()
    snap_cameras(my_cameras)



if __name__ == '__main__':
    main()





