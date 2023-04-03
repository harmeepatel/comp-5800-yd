import string
import heapq
from os import path
import math
import nltk
import numpy as np
import matplotlib.pyplot as plt
import pickle5 as pickle
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import tensorflow as tf

# may have to add
# nltk.download("punkt")
# nltk.download("stopwords")
# nltk.download("wordnet")
# nltk.download('omw-1.4')


def sample(preds, top_n=3):
    preds = np.asarray(preds).astype("float64")
    preds = np.log(preds)
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    return heapq.nlargest(top_n, range(len(preds)), preds.take)


if __name__ == "__main__":
    text_file = open("./aladdin.txt", "r")

    # getting lines and removing whitespaces, newline and punctuations and converting to lower case
    lines = [
        " ".join([line.strip().lower()]).translate(
            str.maketrans("", "", string.punctuation)
        )
        for line in text_file.readlines()
    ]

    # tokenizing each line in lines
    tokens = []
    token_lines = [
        tokens.extend(word_tokenize(line))
        for line in lines
        if word_tokenize(line) != []
    ]

    unique_words = np.unique(tokens)
    unique_word_index = dict((c, i) for i, c in enumerate(unique_words))

    context_len = 5
    next_words = []
    prev_words = []
    for j in range(len(tokens) - context_len):
        prev_words.append(tokens[j: j + context_len])
        next_words.append(tokens[j + context_len])

    X = np.zeros((len(prev_words), context_len, len(unique_words)), dtype=bool)
    Y = np.zeros((len(next_words), len(unique_words)), dtype=bool)
    for i, each_words in enumerate(prev_words):
        for j, each_word in enumerate(each_words):
            X[i, j, unique_word_index[each_word]] = 1
        Y[i, unique_word_index[next_words[i]]] = 1

    model = tf.keras.Sequential()
    model.add(tf.keras.layers.LSTM(128, input_shape=(context_len, len(unique_words))))
    model.add(tf.keras.layers.Dense(len(unique_words)))
    model.add(tf.keras.layers.Activation("softmax"))

    optimizer = tf.keras.optimizers.experimental.RMSprop(learning_rate=0.005)
    model.compile(
        loss="categorical_crossentropy", optimizer=optimizer, metrics=["accuracy"]
    )
    if not path.exists("next_word_model.h5"):
        history = model.fit(
            X, Y, validation_split=0.2, batch_size=32, epochs=128, shuffle=True
        ).history

        model.save("next_word_model.h5")
        pickle.dump(history, open("history.p", "wb"))

    model = tf.keras.models.load_model("next_word_model.h5")
    history = pickle.load(open("history.p", "rb"))

    plt.plot(history["accuracy"])
    plt.plot(history["val_accuracy"])
    plt.title("model accuracy")
    plt.ylabel("accuracy")
    plt.xlabel("epoch")
    plt.legend(["train", "test"], loc="upper left")
    plt.show()

    plt.plot(history["loss"])
    plt.plot(history["val_loss"])
    plt.title("model loss")
    plt.ylabel("loss")
    plt.xlabel("epoch")
    plt.legend(["train", "test"], loc="upper left")
    plt.show()

    q = "one day as he left"
    x = np.zeros((len(q.split(" ")), context_len, len(unique_words)), dtype=bool)
    preds = model.predict(x, verbose=0)[0]
    h = sample(preds=preds)

    print(h)

    # # stemming (eating -> eat)
    # porter = PorterStemmer()
    # tokens = [porter.stem(token) for token in tokens]
    #
    # tf = term_frequency(tokens)
    # idf = inverse_doc_frequency(tf)
    # tfidf = tf_idf(tf, idf)
    # print(tfidf)

    text_file.close()
