from datetime import datetime
from pathlib import Path
from PIL import Image

import requests
import logging
import json
import io
import os


CONF_CAMERAS = 'cameras'
CONF_ROOT_PATH = 'rootdir'

DATE_FORMAT = '%y_%m_%d__%H_%M_%S' 
SNAP_URL = 'http://{}.localdomain/snap.jpeg'
CONFIG_FILE_PATH = '/mnt/geron/timelaps/script/config/cameras.json'

LOGGER_NAME = 'timelaps_logs'
LOG_FILE_NAME = 'timelaps_logs.log'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'


def make_dir(path):
    """
    Checks if 'path' exists and if not creates it

    :param path:    The path we want to make sure exists
    :type path:     str
    """
    if not os.path.exists(path):
        os.mkdir(path)


def get_logger(logger_name, log_path, level=logging.DEBUG):
    """
    Gets a logger for the current session

    :param txt:     The name of our logger
    :type txt:      Path the logs will be written to
    """
    logger = logging.getLogger(logger_name)  
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_path)
    formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def get_snap(ip):
    """
    Returns a snap from the camera in 'ip'

    :param ip:      The ip in which the camera is found
    :type ip:       str
    """
    global logger

    logger.info('trying getting the snapshot from {}'.format(ip))

    # Trying to retrieve the snapshot
    url = SNAP_URL.format(ip)
    try:
        logger.info('sending a get requests for {}'.format(url))
        jpeg = requests.get(url, timeout=5)
    except requests.exceptions.Timeout as e:
        logger.error('{} did not respond ):'.format(ip))
        return None
    except requests.exceptions.RequestException as e:
        logger.error('could not manage to get the snap...\n\t{}'.format(e))
        return None
    except Exception as e:
        logger.error('A new error had occurred!\n\t{}'.format(e))
        return None

    logger.info('got the snapshot with status code {}'.format(jpeg.status_code))

    # Checking if we indeed got the snapshot
    if jpeg.status_code == 200:
        jpeg_raw = jpeg.content
        jpeg_image = Image.open(io.BytesIO(jpeg_raw))

        return jpeg_image
    else:
        logger.error('got an unexpected error code {} instead of 200...'.format(jpeg.status_code))
        return None


def snap_cameras(cam_dict, root_dir):
    """
    Snapping every camera on the list

    :param cam_dict:    A dictionary of the cameras {<name> : <folder_to_save>}
    :type cam_dict:     dict {str : str}
    :param root_dir:    The directory in which we store our images
    :type root_dir:     str
    """
    global logger

    logger.info('going over all of the cameras getting some nice pics :)')

    for camera in cam_dict.keys():
        # The image that we want to save
        my_jpeg = get_snap(camera)

        if my_jpeg is None:
            return

        # The directory to which we shall save the image to
        my_dir = str(Path(root_dir) / Path(cam_dict[camera]))
        make_dir(my_dir)

        # The file name with the current date yo
        my_date_on_path = datetime.now().strftime(DATE_FORMAT)
        my_file = '{}_{}.jpeg'.format(cam_dict[camera], my_date_on_path)

        # The full path!
        my_path = str(Path(my_dir) / Path(my_file))
        my_jpeg.save(my_path)


def main():
    global logger


    with open(CONFIG_FILE_PATH, 'r') as f:
        data = f.read()
    conf = json.loads(data)

    assert CONF_CAMERAS in conf, 'Could not find "{}" in the config file'.format(CONF_CAMERAS)
    assert CONF_ROOT_PATH in conf, 'Could not find "{}" in the config file'.format(CONF_ROOT_PATH)
    assert Path(conf[CONF_ROOT_PATH]).exists(), 'Root path does not exists :('
    
    logger = get_logger(LOGGER_NAME, str(Path(conf[CONF_ROOT_PATH]) / Path(LOG_FILE_NAME)))

    cameras_dict = {}
    for i in conf[CONF_CAMERAS]:
        cameras_dict.update(i)

    snap_cameras(cameras_dict, conf[CONF_ROOT_PATH])


if __name__ == '__main__':
    main()





