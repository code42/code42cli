from os.path import dirname, realpath


def get_save_path():
    return dirname(realpath(__file__))
