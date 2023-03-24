from genericpath import exists
from keras.saving.legacy.save import load_model
import numpy as np
# from numpy.random.mtrand import shuffle
# import tensorflow as tf
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    # Layer,
    Dense,
    Dropout,
    Embedding,
    Attention,
    LSTM,
    # Bidirectional,
)
from tensorflow.keras.datasets import imdb


# class attention(Layer):
#     def __init__(self, return_sequences=True):
#         self.return_sequences = return_sequences
#
#         super(attention, self).__init__()
#
#     def build(self, input_shape):
#         self.W = self.add_weight(
#             name="att_weight", shape=(input_shape[-1], 1), initializer="normal"
#         )
#         self.b = self.add_weight(
#             name="att_bias", shape=(input_shape[1], 1), initializer="normal"
#         )
#         self.b = self.add_weight(name="att_bias", shape=(input_shape[1], 1))
#         self.b = self.add_weight(name="att_bias", shape=(input_shape[1], 1))
#
#         super(attention, self).build(input_shape)
#
#     def call(self, x):
#         e = tf.math.tanh(tf.tensordot(x, self.W, axes=1) + self.b)
#         a = tf.math.softmax(e, axis=1)
#         output = x * a
#         if self.return_sequences:
#
#             return output
#         return tf.math.reduce_sum(output, axis=1).numpy()


def get_bi_lstm_model(X, Y):
    model_file = "./content/bi_lstm"
    if exists(model_file):
        model = load_model(model_file)
        model.summary()
        return model

    model = Sequential()
    model.add(Embedding(n_unique_words, 128, input_length=maxlen))
    model.add(LSTM(64))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.summary()

    model.fit(X, Y, validation_split=0.2, batch_size=32, epochs=16, shuffle=True)
    model.save(model_file)

    return model


def get_bi_lstm_attention_model(X, Y):
    model_file = "./content/bi_lstm_with_attention"
    # if exists(model_file):
    #     model = load_model(model_file)
    #     model.summary()
    #     return model

    model = Sequential()
    model.add(Embedding(n_unique_words, 128, input_length=maxlen))
    model.add(LSTM(64, return_sequences=True))
    model.add(Attention(use_scale=True))  # receive 3D and output 3D
    model.add(Dropout(0.5))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
    model.summary()

    model.fit(X, Y, validation_split=0.2, batch_size=32, epochs=4, shuffle=True)
    model.save(model_file)

    return model


if __name__ == "__main__":
    n_unique_words = 10000
    (x_train, y_train), (x_test, y_test) = imdb.load_data(num_words=n_unique_words)

    maxlen = 200
    x_train = sequence.pad_sequences(x_train, maxlen=maxlen)
    x_test = sequence.pad_sequences(x_test, maxlen=maxlen)
    y_train = np.array(y_train)
    y_test = np.array(y_test)

    # bi_lstm = get_bi_lstm_model(x_train, y_train)
    bi_lstm_with_attention = get_bi_lstm_attention_model(x_train, y_train)

    # bi_lstm_test_acc, bi_lstm_test_loss = bi_lstm.evaluate(x_test, y_test)

    bi_lstm_attention_test_acc, bi_lstm_attention_test_loss = bi_lstm_with_attention.evaluate(
        x_train, y_train)
