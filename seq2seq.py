import os
import numpy as np
import re
import tensorflow as tf
from tensorflow.keras.models import Model
import tensorflow.keras.layers as layers
import unicodedata

# constants
DEV = True
if DEV:
    DATA_PATH = "./data/gtc-small-ic-c.txt"
else:
    DATA_PATH = "./data/gtc-ic-c.txt"

BOS = "[start]"
EOS = "[end]"

NUM_HIDDEN_UNITS = 256
BATCH_SIZE = 64
EPOCHS = 1
STEPS_PER_EPOCHS = 32


def pe(x=""):
    print(x)
    exit()


def read_file():
    """This function returns a numpy array of lines read from file_path. Also removes
    new line character.

    Args:
        file_path: path to file to be read

    Returns:
        numpy.array: numpy array of lines in the file

    """
    def unicodeToAscii(s):
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
        )

    # Lowercase, trim, and remove non-letter characters

    def normalizeString(s):
        s = unicodeToAscii(s.strip())
        s = re.sub(r"([.!?])", r" \1", s)
        s = re.sub(r"[^a-zA-Z.,!?]+", r" ", s)
        return s.strip()

    lines = open(DATA_PATH, encoding='utf-8').read().strip().split('\n')

    # Split every line into pairs and normalize
    source = []
    target = []
    for line in lines:
        source.append(normalizeString(line.split('\t')[0]))
        target.append(normalizeString(line.split('\t')[1]))

    vocab = set()

    for line in source:
        if line == '':
            continue
        for word in line.split():
            for char in word:
                vocab.add(char)
    for line in target:
        if line == '':
            continue
        for word in line.split():
            for char in word:
                vocab.add(char)

    return source, target, {idx: char for idx, char in enumerate(sorted(vocab))}


def vocab_exchange(data, vocab):
    new_data = []
    for line in data:
        tmp = []
        for char in line:
            if char == ' ':
                continue
            tmp.append(vocab[char])
        new_data.append(tmp)
    return new_data


def data_factory(inputs, shape, index, is_target=False):

    data = np.zeros(shape, dtype='float32')

    for idx, input in enumerate(inputs):
        for timestep, word in enumerate(input.split()):
            if timestep > 0 and is_target:
                data[idx, timestep - 1, index[word]] = 1.
            else:
                data[idx, timestep, index[word]] = 1.

    return data


if __name__ == "__main__":

    source, target, int_to_char = read_file()
    char_to_int = {value: key for key, value in int_to_char.items()}

    source_vec = vocab_exchange(source, char_to_int)
    target_vec = vocab_exchange(target, char_to_int)

    pe(source_vec[:5])

