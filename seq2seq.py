import random
import re
import unicodedata

DEV = True
if DEV:
    DATA_PATH = './data/gtc-small-%s-%s.txt'
else:
    DATA_PATH = './data/gtc-%s-%s.txt'

EOS_token = 1
MAX_LENGTH = 200
SOS_token = 0


def main():
    input_lang, output_lang, pairs = readLangs('incorrect', 'correct', False)
    # print(input_lang.word2count)


class Lang:
    def __init__(self, name):
        self.name = name
        self.word2index = {}
        self.word2count = {}
        self.index2word = {0: "SOS", 1: "EOS"}
        self.n_words = 2  # Count SOS and EOS

    def addSentence(self, sentence):
        for word in sentence.split(' '):
            self.addWord(word)

    def addWord(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.n_words
            self.word2count[word] = 1
            self.index2word[self.n_words] = word
            self.n_words += 1
        else:
            self.word2count[word] += 1


def unicodeToAscii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


# Lowercase, trim, and remove non-letter characters


def normalizeString(s):
    s = unicodeToAscii(s.lower().strip())
    s = re.sub(r"([.!?])", r" \1", s)
    s = re.sub(r"[^a-zA-Z.!?]+", r" ", s)
    return s


def readLangs(input_class, output_class, reverse=False):
    print("Reading lines...")

    # Read the file and split into lines
    lines = open(DATA_PATH % (input_class, output_class), encoding='utf-8').\
        read().strip().split('\n')

    # Split every line into pairs and normalize
    pairs = [[normalizeString(s) for s in line.split('\t')] for line in lines]

    # Reverse pairs, make Lang instances
    if reverse:
        pairs = [list(reversed(p)) for p in pairs]
        input_lang = Lang(output_class)
        output_lang = Lang(input_class)
    else:
        input_lang = Lang(input_class)
        output_lang = Lang(output_class)

    for pair in pairs:
        input_lang.addSentence(pair[0])
        output_lang.addSentence(pair[1])

    print("Counted words:")
    print(input_lang.name, ":", input_lang.n_words)
    print(output_lang.name, ":", output_lang.n_words)

    return input_lang, output_lang, pairs


# def filterPair(p):
#     return len(p[0].split(' ')) < MAX_LENGTH and \
#         len(p[1].split(' ')) < MAX_LENGTH


# def filterPairs(pairs):
#     # return [pair for pair in pairs if filterPair(pair)]
#     return [pair for pair in pairs]


if __name__ == "__main__":
    main()
