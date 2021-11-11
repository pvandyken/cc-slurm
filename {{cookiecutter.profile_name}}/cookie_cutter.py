#
# Based on lsf CookieCutter.py
#
import os
import json

d = os.path.dirname(__file__)
with open(os.path.join(d, "settings.json")) as fh:
    settings = json.load(fh)


class CookieCutter:

    CLUSTER_NAME = settings['CLUSTER_NAME']
    MAX_TIME = int(settings['MAX_TIME'])
    DEFAULT_TIME = int(settings['DEFAULT_TIME'])
    MAX_MEM_MB = int(settings['MAX_MEM_MB'])
    DEFAULT_MEM_MB = int(settings['DEFAULT_MEM_MB'])
    MAX_GPUS = int(settings['MAX_GPUS'])
    MAX_THREADS = int(settings['MAX_THREADS'])
    ACCOUNT = settings['ACCOUNT']
    TEST_MODE = settings['TEST_MODE']

    @staticmethod
    def get_cluster_option() -> str:
        cluster = CookieCutter.CLUSTER_NAME
        if cluster != "":
            return f"--cluster={cluster}"
        return ""