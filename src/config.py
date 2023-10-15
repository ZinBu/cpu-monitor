import os
from enum import Enum


REFRESH_TIMEOUT_SEC = 1.0
DIGIT_SIZE = 45
ONE_DIGIT_POS = 0
TWO_DIGIT_POS = 20
MAP_SIZE = 64, 64
LINUX_PLATFORM = 'linux'

FONT = 'Arial'
ICON_BG = 'transparent'

MSG_DURATION_DEFAULT_MS = 2000
MSG_DURATION_MS = 100
COLOR_SET_MSG = 'Color set: '
CLOSE_MSG = 'Close'

DB_DIR = '_db'
DB_NAME = os.path.join(DB_DIR, 'config')


class Colors(Enum):
    Auto = None
    Red = (255, 0, 0)
    MediumVioletRed = (199, 21, 133)
    DeepPink = (255, 20, 147)
    OrangeRed = (255, 69, 0)
    DarkOrange = (255, 140, 0)
    PapayaWhip = (255, 239, 213)
    MediumOrchid = (186, 85, 211)
    PaleGreen = (152, 251, 152)
    Lime = (0, 255, 0)
    MediumSlateBlue = (123, 104, 238)
    DeepSkyBlue = (0, 191, 255)
    SteelBlue = (30, 144, 255)
