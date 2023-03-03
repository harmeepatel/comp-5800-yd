import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow_text as tf_text
import tensorflow.keras.models as models
import tensorflow.keras.layers as layers

# constants
DEV = True
CORRECT_PATH = "./data/gmeg/dev/d/clean.txt"
INCORRECT_PATH = "./data/gmeg/dev/d/corrupt.txt"
EPOCHS = 16
BATCH_SIZE = 64
MAX_VOCAB_SIZE = 5000


def read_file(file_path: str):
    """This function returns a numpy array of lines read from file_path. Also removes
    new line character.

    Args:
        file_path: path to file to be read

    Returns:
        numpy.array: numpy array of lines in the file

    """
    with open(file_path, "r") as f:
        return np.array([lines.replace("\n", "") for lines in f.readlines()])


def sentence_from_tokens(vectorizers, tokens):
    """Returns a sentence from an array of tokens

    Args:
        vectorizers: the vectorizer to be used to convert tokens into sentence
        tokens: the tokens to be converted to sentence

    Returns:
        str: sentence from tokens
    """
    corv = np.array(vectorizers.get_vocabulary())
    tok = corv[tokens[0].numpy()]
    return ' '.join(tok)


def lower_and_split_punct(text):
    # Split accented characters.
    text = tf_text.normalize_utf8(text, 'NFKD')
    text = tf.strings.lower(text)
    # Keep space, a to z, and select punctuation.
    text = tf.strings.regex_replace(text, '[^ a-z.?!,¿]', '')
    # Add spaces around punctuation.
    text = tf.strings.regex_replace(text, '[.?!,¿]', r' \0 ')
    # Strip whitespace.
    text = tf.strings.strip(text)

    text = tf.strings.join(['[START]', text, '[END]'], separator=' ')
    return text


def process_text(inn, out):
    context = correct_vectorizer(inn).to_tensor()
    target = incorrect_vectorizer(out)
    target_in = target[:, :-1].to_tensor()
    target_out = target[:, 1:].to_tensor()
    return (context, target_in), target_out


if __name__ == "__main__":
    # reading files as np.array
    correct = read_file(CORRECT_PATH)
    incorrect = read_file(INCORRECT_PATH)

    # buffer size and batch size for tf.data.Dataset
    BUFFER_SIZE = len(correct)

    # 80-20 train-test split
    np.random.seed(128)
    train_test_split = np.random.uniform(size=(len(incorrect),)) < 0.8
    # creating dataset
    if DEV:
        train_raw = (
            tf.data.Dataset
            .from_tensor_slices((correct[train_test_split], incorrect[train_test_split]))
            .batch(BATCH_SIZE)
        )
        val_raw = (
            tf.data.Dataset
            .from_tensor_slices((correct[~train_test_split], incorrect[~train_test_split]))
            .batch(BATCH_SIZE)
        )
    else:
        train_raw = (
            tf.data.Dataset
            .from_tensor_slices((correct[train_test_split], incorrect[train_test_split]))
            .shuffle(BUFFER_SIZE)
            .batch(BATCH_SIZE)
        )
        val_raw = (
            tf.data.Dataset
            .from_tensor_slices((correct[~train_test_split], incorrect[~train_test_split]))
            .shuffle(BUFFER_SIZE)
            .batch(BATCH_SIZE)
        )

    # print(f"train_raw[0]:\n{list(train_raw.as_numpy_iterator())[0]}")

    # defining text-vectorizers
    correct_vectorizer = tf.keras.layers.TextVectorization(
        standardize=lower_and_split_punct,
        max_tokens=MAX_VOCAB_SIZE,
        ragged=True
    )
    incorrect_vectorizer = tf.keras.layers.TextVectorization(
        standardize=lower_and_split_punct,
        max_tokens=MAX_VOCAB_SIZE,
        ragged=True
    )

    # adapting vectorizers to vocab
    correct_vectorizer.adapt(train_raw.map(lambda c, ic: c))
    incorrect_vectorizer.adapt(train_raw.map(lambda c, ic: ic))
    # print(correct_vectorizer.get_vocabulary()[:10])
    # print(incorrect_vectorizer.get_vocabulary()[:10])

    if DEV:
        example_tokens = correct_vectorizer(
            list(train_raw.as_numpy_iterator())[0][0])

        eg = sentence_from_tokens(correct_vectorizer, example_tokens)
        print(eg)

        plt.subplot(1, 2, 1)
        plt.pcolormesh(example_tokens.to_tensor())
        plt.title('Token IDs')

        plt.subplot(1, 2, 2)
        plt.pcolormesh(example_tokens.to_tensor() != 0)
        plt.title('Mask')

    if not DEV:
        plt.show()

    train_ds = train_raw.map(process_text, tf.data.AUTOTUNE)
    val_ds = val_raw.map(process_text, tf.data.AUTOTUNE)
    # (encoder_input_data, decoder_input_data), decoder_target_data = train_ds.get_single_element()
    print(train_ds.get_single_element())

    if DEV:
        for (ex_context_tok, ex_tar_in), ex_tar_out in train_ds:
            print(
                f"sentence_from_tokens:\n {sentence_from_tokens(correct_vectorizer, ex_context_tok)}")
            print(f"ex_tar_in:\n {sentence_from_tokens(correct_vectorizer, ex_tar_in)}")
            print(f"ex_tar_out:\n {sentence_from_tokens(correct_vectorizer, ex_tar_out)}")
            break

    encoder_vocab = 2000
    decoder_vocab = 2000

    encoder_input = layers.Input(shape=(None,))
    encoder_embedded = layers.Embedding(input_dim=encoder_vocab, output_dim=64)(
        encoder_input
    )

# Return states in addition to output
    output, state_h, state_c = layers.LSTM(64, return_state=True, name="encoder")(
        encoder_embedded
    )
    encoder_state = [state_h, state_c]

    decoder_input = layers.Input(shape=(None,))
    decoder_embedded = layers.Embedding(input_dim=decoder_vocab, output_dim=64)(
        decoder_input
    )

# Pass the 2 states to a new LSTM layer, as initial state
    decoder_output = layers.LSTM(64, name="decoder")(
        decoder_embedded, initial_state=encoder_state
    )
    output = layers.Dense(10)(decoder_output)

    model = models.Model([encoder_input, decoder_input], output)
    model.summary()
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy')
    model.fit([encoder_input_data, decoder_input_data], decoder_target_data,
              batch_size=BATCH_SIZE,
              epochs=EPOCHS,
              validation_split=0.2)
# model.compile(optimizer='adam',
#               loss='sparse_categorical_crossentropy',
#               metrics=['accuracy']
#               )
# model.fit(train_ds,
#           epochs=16,
#           validation_data=val_ds,
#           shuffle=True,
#           steps_per_epoch=100,
#           validation_steps=100,
#           workers=4,
#           use_multiprocessing=True
#           )
