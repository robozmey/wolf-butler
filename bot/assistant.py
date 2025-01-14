from yandex_cloud_ml_sdk import YCloudML


import re
import os
from dotenv import load_dotenv

load_dotenv()

YANDEX_FOLDER= os.getenv('YANDEX_CLOUD_FOLDER')
YANDEX_TOKEN = os.getenv('YANDEX_CLOUD_TOKEN')