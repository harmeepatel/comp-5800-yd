import getopt
import numpy as np
import os
import sys


# constants
DEV = False
opts, _ = getopt.getopt(sys.argv[1:], "d", [])
for opt, _ in opts:
    if opt == '-d':
        DEV = True


if DEV:
    CORRECT_PATH = "../data/d/small-clean.txt"
    INCORRECT_PATH = "../data/d/small-corrupt.txt"
else:
    CORRECT_PATH = "../data/d/clean.txt"
    INCORRECT_PATH = "../data/d/corrupt.txt"

ENCODER_INPUT_PATH = "./data-array/encoder_input.npy"
DECODER_INPUT_PATH = "./data-array/decoder_input.npy"
DECODER_OUTPUT_PATH = "./data-array/decoder_output.npy"
MAX_CHAR_LEN = 8
BOS = '∫'
EOS = 'µ'
PAD = 'ƒ'


def pad(input):
    """Pad the input list with [[ PAD * MAX_CHAR_LEN ]] for fixed input length

    Args:
        input ([[[char]]]): list to be padded

    Returns:
        input ([[[char]]]): padded list

    """
    for i in range(len(input)):
        tmp = [list(PAD * MAX_CHAR_LEN)] * (max_line_len - len(input[i]))
        input[i] = input[i] + tmp
    return input


def char_to_int(data):
    for i in range(len(data)):
        for j in range(len(data[i])):
            # print(f"data[{i}][{j}]: {data[i][j]}")
            data[i][j] = [char_idx[char] for char in data[i][j]]

    return data


input_vocab = set()
input_vocab.add(BOS)
input_vocab.add(EOS)
input_vocab.add(PAD)

correct_lines = []
if os.path.isfile(CORRECT_PATH):
    with open(CORRECT_PATH, "r", encoding="utf-8") as f:
        correct_lines = [line.lower() for line in f.read().split("\n")]
        for line in correct_lines:
            for char in line:
                input_vocab.add(char)

incorrect_lines = []
if os.path.isfile(INCORRECT_PATH):
    with open(INCORRECT_PATH, "r", encoding="utf-8") as f:
        incorrect_lines = [line.lower() for line in f.read().split("\n")]
        for line in incorrect_lines:
            for char in line:
                input_vocab.add(char)

char_idx = dict(zip(sorted(input_vocab), [i for i, _ in enumerate(sorted(input_vocab))]))
idx_char = {v: k for k, v in char_idx.items()}

max_line_len = max([
    max([len(line) for line in correct_lines]),
    max([len(line) for line in incorrect_lines]),
])
while max_line_len % 4 != 0:
    max_line_len += max_line_len % 4


encoder_input = []
for line in incorrect_lines:
    tmp = []
    for i in range(len(line)):
        char_list = line[i:i + MAX_CHAR_LEN]
        if len(char_list) < MAX_CHAR_LEN:
            t = char_list + PAD * (MAX_CHAR_LEN - len(char_list))
            tmp.append(list(t))
            continue
        tmp.append(list(char_list))
    encoder_input.append(tmp)

decoder_input = []
decoder_output = []
for line in correct_lines:
    di_tmp = []
    do_tmp = []
    for i in range(len(line)):
        di_char_list = BOS + line[i:i + MAX_CHAR_LEN - 1]
        do_char_list = line[i:i + MAX_CHAR_LEN - 1] + EOS

        if len(di_char_list) < MAX_CHAR_LEN:
            t1 = di_char_list + PAD * (MAX_CHAR_LEN - len(di_char_list))
            t2 = do_char_list + PAD * (MAX_CHAR_LEN - len(do_char_list))
            di_tmp.append(list(t1))
            do_tmp.append(list(t2))
        else:
            di_tmp.append(list(di_char_list))
            do_tmp.append(list(do_char_list))
    decoder_input.append(di_tmp)
    decoder_output.append(do_tmp)

encoder_input = pad(encoder_input)
decoder_input = pad(decoder_input)
decoder_output = pad(decoder_output)

encoder_input = char_to_int(encoder_input)
decoder_input = char_to_int(decoder_input)
decoder_output = char_to_int(decoder_output)

idx = 0
# print(len(encoder_input[idx]), '\n')
# print(encoder_input[idx], '\n')
# print(len(decoder_input[idx]), '\n')
# print(decoder_input[idx], '\n')
# print(len(decoder_output[idx]), '\n')
# print(decoder_output[idx], '\n')

# print(f"ord({BOS}): {ord(BOS)}")
# print(f"ord({EOS}): {ord(EOS)}")
# print(f"ord({PAD}): {ord(PAD)}")


with open(ENCODER_INPUT_PATH, 'wb') as f:
    np.save(f, encoder_input)

with open(DECODER_INPUT_PATH, 'wb') as f:
    np.save(f, decoder_input)

with open(DECODER_OUTPUT_PATH, 'wb') as f:
    np.save(f, decoder_output)
