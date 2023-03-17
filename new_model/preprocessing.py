import const as c
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
    CORRECT_PATH = c.CORRECT_PATH_DEV
    INCORRECT_PATH = c.INCORRECT_PATH_DEV
else:
    CORRECT_PATH = c.CORRECT_PATH
    INCORRECT_PATH = c.INCORRECT_PATH


def pad(input):
    """Pad the input list with [[ PAD * MAX_CHAR_LEN ]] for fixed input length

    Args:
        input ([[[char]]]): list to be padded

    Returns:
        input ([[[char]]]): padded list

    """
    for i in range(len(input)):
        tmp = [list(c.PAD * c.MAX_CHAR_LEN)] * (max_line_len - len(input[i]))
        input[i] = input[i] + tmp
    return input


def char_to_int(data):
    """convert char to int with char_idx as dictionary.

    Args:
        data ([[[char]]]): list to be converted

    Returns:
        data ([[[int]]]): converted list

    """
    for i in range(len(data)):
        for j in range(len(data[i])):
            # print(f"data[{i}][{j}]: {data[i][j]}")
            data[i][j] = [char_idx[char] for char in data[i][j]]

    return data


def save_npy(path, data):
    """save data to file.

    Args:
        path (str): file path
        data ([[[int]]]): data to be saved
    """
    with open(path, 'wb') as f:
        np.save(f, data)


# char-vocab of corpus
input_vocab = set()
input_vocab.add(c.BOS)
input_vocab.add(c.EOS)
input_vocab.add(c.PAD)

# read lines from correct.txt
correct_lines = []
if os.path.isfile(CORRECT_PATH):
    with open(CORRECT_PATH, "r", encoding="utf-8") as f:
        correct_lines = [line.lower() for line in f.read().split("\n")]
        for line in correct_lines:
            for char in line:
                input_vocab.add(char)

# read lines from incorrect.txt
incorrect_lines = []
if os.path.isfile(INCORRECT_PATH):
    with open(INCORRECT_PATH, "r", encoding="utf-8") as f:
        incorrect_lines = [line.lower() for line in f.read().split("\n")]
        for line in incorrect_lines:
            for char in line:
                input_vocab.add(char)

# char index
char_idx = dict(zip(sorted(input_vocab), [i for i, _ in enumerate(sorted(input_vocab))]))
idx_char = {v: k for k, v in char_idx.items()}

# max num chars in a sentence
max_line_len = max([
    max([len(line) for line in correct_lines]),
    max([len(line) for line in incorrect_lines]),
])
# making the number divisible by 4 (gives error in model.py if not done)
while max_line_len % 4 != 0:
    max_line_len += max_line_len % 4

# creating inputs
encoder_input = []
for line in incorrect_lines:
    tmp = []
    for i in range(len(line)):
        char_list = line[i:i + c.MAX_CHAR_LEN]
        if len(char_list) < c.MAX_CHAR_LEN:
            t = char_list + c.PAD * (c.MAX_CHAR_LEN - len(char_list))
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
        di_char_list = c.BOS + line[i:i + c.MAX_CHAR_LEN - 1]
        do_char_list = line[i:i + c.MAX_CHAR_LEN - 1] + c.EOS

        if len(di_char_list) < c.MAX_CHAR_LEN:
            t1 = di_char_list + c.PAD * (c.MAX_CHAR_LEN - len(di_char_list))
            t2 = do_char_list + c.PAD * (c.MAX_CHAR_LEN - len(do_char_list))
            di_tmp.append(list(t1))
            do_tmp.append(list(t2))
        else:
            di_tmp.append(list(di_char_list))
            do_tmp.append(list(do_char_list))
    decoder_input.append(di_tmp)
    decoder_output.append(do_tmp)

# padding and converting inputs to ints inputs
encoder_input = np.array(char_to_int(pad(encoder_input)))
decoder_input = np.array(char_to_int(pad(decoder_input)))
decoder_output = np.array(char_to_int(pad(decoder_output)))

# split idx
np.random.seed(128)
train_test_split = np.random.uniform(size=(len(encoder_input),)) < 0.8

# train split
encoder_input_train = encoder_input[train_test_split]
decoder_input_train = decoder_input[train_test_split]
decoder_output_train = decoder_output[train_test_split]

# test split
encoder_input_test = encoder_input[~train_test_split]
decoder_input_test = decoder_input[~train_test_split]
decoder_output_test = decoder_output[~train_test_split]

# # split idx
# train_val_split = np.random.uniform(size=(len(encoder_input_train),)) < 0.8
# # validation split
# encoder_input_val = encoder_input_train[~train_val_split]
# decoder_input_val = decoder_input_train[~train_val_split]
# decoder_output_val = decoder_output_train[~train_val_split]
#
# encoder_input_train = encoder_input_train[train_val_split]
# decoder_input_train = decoder_input_train[train_val_split]
# decoder_output_train = decoder_output_train[train_val_split]


save_npy(c.ENCODER_INPUT_PATH, encoder_input)
save_npy(c.DECODER_INPUT_PATH, decoder_input)
save_npy(c.DECODER_OUTPUT_PATH, decoder_output)

save_npy(c.ENCODER_INPUT_TRAIN_PATH, encoder_input_train)
save_npy(c.DECODER_INPUT_TRAIN_PATH, decoder_input_train)
save_npy(c.DECODER_OUTPUT_TRAIN_PATH, decoder_output_train)

# save_npy(c.ENCODER_INPUT_VAL_PATH, encoder_input_val)
# save_npy(c.DECODER_INPUT_VAL_PATH, decoder_input_val)
# save_npy(c.DECODER_OUTPUT_VAL_PATH, decoder_output_val)

save_npy(c.ENCODER_INPUT_TEST_PATH, encoder_input_test)
save_npy(c.DECODER_INPUT_TEST_PATH, decoder_input_test)
save_npy(c.DECODER_OUTPUT_TEST_PATH, decoder_output_test)
