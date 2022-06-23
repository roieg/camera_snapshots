from datetime import datetime
from PIL import Image

import requests
import json
import io
import os

DEBUGGING = False

CONF_CAMERAS = 'cameras'
CONF_ROOT_PATH = 'rootdir'
CONF_DEBUGGING = 'debug'

DATE_FORMAT = '%y_%m_%d__%H_%M_%S' 
CONFIG_FILE_PATH = ''

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
        jpeg = requests.get('http://{}.localdomain/snap.jpeg'.format(ip), timeout=5)
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


def snap_cameras(cam_dict, root_dir):
    """
    Snapping every camera on the list

    :param cam_dict:    A dictionary of the cameras {<name> : <folder_to_save>}
    :type cam_dict:     dict {str : str}
    :param root_dir:    The directory in which we store our images
    :type root_dir:     str
    """
    for camera in cam_dict.keys():
        # The image that we want to save
        my_jpeg = get_snap(camera)

        # The directory to which we shall save the image to
        my_dir = os.path.join(root_dir, cam_dict[camera])
        make_dir(my_dir)

        # The file name with the current date yo
        my_date_on_path = datetime.now().strftime(DATE_FORMAT)
        my_file = '{}_{}.jpeg'.format(cam_dict[camera], my_date_on_path)

        # The full path!
        my_path = os.path.join(my_dir, my_file)

        # If we managed to get the file
        if my_jpeg:
            my_jpeg.save(my_path)


def remap_keys(cam_dict):
    for key in list(cam_dict.keys()):
        new_key = key.replace(' ', '-')
        if new_key not in cam_dict:
            cam_dict[new_key] = cam_dict[key]
            del cam_dict[key]


def main():
    global DEBUGGING

    with open(CONFIG_FILE_PATH, 'r') as f:
        data = f.read()
    conf = json.loads(data)

    assert CONF_CAMERAS in conf, 'Could not find "{}" in the config file'.format(CONF_CAMERAS)
    assert CONF_ROOT_PATH in conf, 'Could not find "{}" in the config file'.format(CONF_ROOT_PATH)
    print(conf[CONF_ROOT_PATH])
    assert os.path.exists(conf[CONF_ROOT_PATH]), 'Root path does not exists :('

    DEBUGGING = True if CONF_DEBUGGING in conf and conf[CONF_DEBUGGING].lower() == 'true' else False
    pprint('We are debugging!')

    cameras_dict = {}
    for i in conf[CONF_CAMERAS]:
        cameras_dict.update(i)

    remap_keys(cameras_dict)

    snap_cameras(cameras_dict, conf[CONF_ROOT_PATH])



if __name__ == '__main__':
    main()





