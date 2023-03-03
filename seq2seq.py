import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
import tensorflow.keras.layers as layers

# constants
DEV = True
CORRECT_PATH = "./data/gmeg/dev/d/clean.txt"
INCORRECT_PATH = "./data/gmeg/dev/d/corrupt.txt"
BOS = "[start]"
EOS = "[end]"

NUM_HIDDEN_UNITS = 256
BATCH_SIZE = 64
EPOCHS = 1
STEPS_PER_EPOCHS = 32


def pe(x=""):
    print(x)
    exit()


def read_file(file: str, is_target=False):
    """This function returns a numpy array of lines read from file_path. Also removes
    new line character.

    Args:
        file_path: path to file to be read

    Returns:
        numpy.array: numpy array of lines in the file

    """
    lines = []
    if os.path.isfile(file):
        with open(file, "r", encoding="utf-8") as f:
            lines = f.read().split("\n")
    else:
        lines.append(file)

    texts = []
    input_vocab = set()

    for line in lines:
        if is_target:
            line = BOS + ' ' + line + ' ' + EOS
        texts.append(line)
        for word in line.split():
            if word not in input_vocab:
                input_vocab.add(word)

    return texts, sorted(list(input_vocab))


def inference_translater(input):

    encoder_states = encoder_model.predict(input)

    output_seq = np.zeros((1, 1, decoder_vocab_size))
    output_seq[0, 0, target_word2idx[BOS]] = 1.

    stop_condition = False
    output_sentence = ""
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict([output_seq] + encoder_states)

        sampled_token_index = np.argmax(output_tokens[0, -1, :])

        sampled_char = target_idx2word[sampled_token_index]
        output_sentence += sampled_char

        if (sampled_char == EOS or len(output_sentence) > max_decoder_seq_length):
            stop_condition = True

        output_seq = np.zeros((1, 1, decoder_vocab_size))
        output_seq[0, 0, sampled_token_index] = 1.

        encoder_states = [h, c]

    return output_sentence


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

    input_texts, input_vocab = read_file(CORRECT_PATH)
    target_texts, target_vocab = read_file(CORRECT_PATH, is_target=True)

    encoder_vocab_size = len(input_vocab)
    decoder_vocab_size = len(target_vocab)

    max_encoder_seq_length = max([len(text.split()) for text in input_texts])
    max_decoder_seq_length = max([len(text.split()) for text in target_texts])

    input_word2idx = dict([(word, idx) for idx, word in enumerate(input_vocab)])
    target_word2idx = dict([(word, idx) for idx, word in enumerate(target_vocab)])

    input_idx2word = dict([(idx, word) for word, idx in input_word2idx.items()])
    target_idx2word = dict([(idx, word) for word, idx in target_word2idx.items()])

    encoder_input_data_shape = (len(input_texts), max_encoder_seq_length, encoder_vocab_size)
    decoder_input_data_shape = (len(input_texts), max_decoder_seq_length, decoder_vocab_size)
    decoder_target_data_shape = (len(target_texts), max_decoder_seq_length, decoder_vocab_size)

    encoder_input_data = data_factory(input_texts, encoder_input_data_shape, input_word2idx)
    decoder_input_data = data_factory(target_texts, decoder_input_data_shape, target_word2idx)
    decoder_target_data = data_factory(target_texts, decoder_target_data_shape,
                                       target_word2idx, is_target=True)

    # training
    # encoder
    encoder_inputs = layers.Input(shape=(None, encoder_vocab_size))
    encoder_lstm = layers.LSTM(units=NUM_HIDDEN_UNITS, return_state=True)

    __encoder_outputs, state_h, state_c = encoder_lstm(encoder_inputs)
    encoder_states = [state_h, state_c]

    # decoder
    decoder_inputs = layers.Input(shape=(None, decoder_vocab_size))
    decoder_lstm = layers.LSTM(
        units=NUM_HIDDEN_UNITS,
        return_sequences=True,
        return_state=True
    )

    decoder_outputs, __de_state_h, __de_state_c = decoder_lstm(
        decoder_inputs,
        initial_state=encoder_states
    )
    decoder_softmax_layer = layers.Dense(decoder_vocab_size, activation='softmax')
    decoder_outputs = decoder_softmax_layer(decoder_outputs)

    # model
    model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
    model.compile(optimizer="rmsprop",
                  loss="categorical_crossentropy",
                  metrics=['accuracy'],
                  )
    model.summary()
    model.fit(
        x=[encoder_input_data, decoder_input_data],
        y=decoder_target_data,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        # steps_per_epoch=STEPS_PER_EPOCHS,
        validation_split=0.2
    )
    model.save("./saved-models/seq2seq_translate_model")

    # inference
    encoder_model = Model(encoder_inputs, encoder_states)

    decoder_state_input_h = layers.Input(shape=(NUM_HIDDEN_UNITS))
    decoder_state_input_c = layers.Input(shape=(NUM_HIDDEN_UNITS))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_inputs, initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_outputs = decoder_softmax_layer(decoder_outputs)
    decoder_model = Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs] + decoder_states
    )
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
    model.summary()
    print(decoder_states_inputs)

    # text = "I am so tried and I feel bored to go home ."
    text = "I used to tennis when I was university student . "
    text, _ = read_file(text)
    text = data_factory(text, encoder_input_data_shape, input_word2idx)

    inference_translater(text)
