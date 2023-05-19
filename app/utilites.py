import os
import tempfile


def get_tmp_folder():
    tmp_folder = tempfile.gettempdir()

    if os.getenv("TMP_CUSTOM_DIR", None):
        tmp_folder = os.getenv("TMP_CUSTOM_DIR", None)

    return tmp_folder