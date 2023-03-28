import const as c
import getopt
import numpy as np
import os
import sys
import json


# constants
DEV = False
opts, _ = getopt.getopt(sys.argv[1:], "d", [])
for opt, _ in opts:
    if opt == '-d':
        DEV = True


if DEV:
    PATH = c.SGTC
else:
    PATH = c.GITHUB_TYPO_CORPUS


def save_npy(path, data):
    """save data to file.

    Args:
        path (str): file path
        data ([[[int]]]): data to be saved
    """
    [dir, file] = path.split('/')[1:]
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if not os.path.isfile(file):
        open(path, 'w').close()

    with open(path, 'wb') as f:
        np.save(f, data)


if __name__ == "__main__":
    data = []
    with open(PATH, 'r') as file:
        for line in file:
            data.append(json.loads(line))

    for i in data:
        print(json.dumps(i, indent=4))
