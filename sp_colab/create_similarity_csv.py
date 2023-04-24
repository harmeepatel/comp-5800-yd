import datetime
import pandas as pd
import spacy
import time
import os
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction

DEV = False

# spellgram
SPG_DATA_PATH = "/content/sp_colab/data/spellgram.csv"
if DEV:
    SPG_PREDICTED = "/content/sp_colab/data/predicted/spellgram-predicted-50.txt"
    SPG_CSV_PATH = "/content/sp_colab/data/csv/spg-small-similarity.csv"
else:
    SPG_PREDICTED = "/content/sp_colab/data/predicted/spellgram-predicted-40000.txt"
    SPG_CSV_PATH = "/content/sp_colab/data/csv/spg-similarity.csv"

# github-typo-corpus
GTC_CORRECT = "/content/sp_colab/data/gtc-correct.txt"
GTC_INCORRECT = "/content/sp_colab/data/gtc-incorrect.txt"
# GTC_PREDICTED = "/content/sp_colab/data/gtc-predicted.txt"
if DEV:
    GTC_CUS_CSV_PATH = "/content/sp_colab/data/csv/gtc-small-custom-similarity.csv"
    GTC_CUS_PREDICTED = "/content/sp_colab/data/gtc-custom-predicted.txt"
    GTC_CSV_PATH = "/content/sp_colab/data/csv/gtc-small-similarity.csv"
    GTC_PREDICTED = "/content/sp_colab/data/gtc-predicted-small.txt"
else:
    GTC_CSV_PATH = "/content/sp_colab/data/csv/gtc-similarity.csv"
    GTC_CUS_CSV_PATH = "/content/sp_colab/data/csv/gtc-custom-similarity.csv"
    GTC_PREDICTED = "/content/sp_colab/data/gtc-predicted.txt"
    GTC_CUS_PREDICTED = "/content/sp_colab/data/gtc-custom-predicted.txt"


W = (.33, .33, .33, 0)
smoothie = SmoothingFunction().method3

nlp = spacy.load("en_core_web_lg")


def read_file(path):
    lines = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    return lines


def filter_none(data):
    return list(filter(lambda i: i is not None, data))


def create_csv(correct, incorrect, predicted, path):
    st = time.time()
    ue = 0
    ui = 50
    t = time.time()
    iter_sec = 0
    data_len = min(len(correct), len(incorrect), len(predicted))
    lines = {
        'correct': data_len * [None],
        'incorrect': data_len * [None],
        'predicted': data_len * [None],
        'c-i-sim-spacy': data_len * [None],
        'c-p-sim-spacy': data_len * [None],
        'i-p-sim-spacy': data_len * [None],
        'c-i-sim-bleu': data_len * [None],
        'c-p-sim-bleu': data_len * [None],
        'i-p-sim-bleu': data_len * [None],
    }
    prev = {
        'correct': "",
        'incorrect': "",
        'predicted': "",
    }

    for i in range(data_len):
        if DEV:
            if ue == 255:
                break
        c_line = str(correct[i]).strip()
        i_line = str(incorrect[i]).strip()
        p_line = str(predicted[i]).strip()

        if i > 0:
            if prev['correct'] == c_line or prev['incorrect'] == i_line or prev['predicted'] == p_line:
                prev['correct'] = c_line
                prev['incorrect'] = i_line
                prev['predicted'] = p_line
                continue
        prev['correct'] = c_line
        prev['incorrect'] = i_line
        prev['predicted'] = p_line

        lines['correct'][i] = c_line
        lines['incorrect'][i] = i_line
        lines['predicted'][i] = p_line

        # using spacy en_core_web_lg for similarity
        cor_vec_spc = nlp(c_line)
        inc_vec_spc = nlp(i_line)
        pre_vec_spc = nlp(p_line)

        lines['c-i-sim-spacy'][i] = cor_vec_spc.similarity(inc_vec_spc)
        lines['c-p-sim-spacy'][i] = cor_vec_spc.similarity(pre_vec_spc)
        lines['i-p-sim-spacy'][i] = inc_vec_spc.similarity(pre_vec_spc)

        # using bleu score from nltk
        c = [c_line.split()]
        ii = [i_line.split()]
        io = i_line.split()
        p = p_line.split()

        lines['c-i-sim-bleu'][i] = sentence_bleu(c, io, weights=W, smoothing_function=smoothie)
        lines['c-p-sim-bleu'][i] = sentence_bleu(c, p, weights=W, smoothing_function=smoothie)
        lines['i-p-sim-bleu'][i] = sentence_bleu(ii, p, weights=W, smoothing_function=smoothie)

        if ue % ui == 0:
            iter_sec = ui / (time.time() - t)
            t = time.time()
        print(f"{i} / {data_len} [ {round(iter_sec, 4)} itr/s ]", end='\r', flush=True)
        ue += 1

    lines['correct'] = filter_none(lines['correct'])
    lines['incorrect'] = filter_none(lines['incorrect'])
    lines['predicted'] = filter_none(lines['predicted'])
    lines['c-i-sim-spacy'] = filter_none(lines['c-i-sim-spacy'])
    lines['c-p-sim-spacy'] = filter_none(lines['c-p-sim-spacy'])
    lines['i-p-sim-spacy'] = filter_none(lines['i-p-sim-spacy'])
    lines['c-i-sim-bleu'] = filter_none(lines['c-i-sim-bleu'])
    lines['c-p-sim-bleu'] = filter_none(lines['c-p-sim-bleu'])
    lines['i-p-sim-bleu'] = filter_none(lines['i-p-sim-bleu'])

    os.makedirs(os.path.dirname(path), exist_ok=True)
    pd.DataFrame(lines).to_csv(path, index=False)
    print(f"\n\n___ written {path} ___\ntime taken: {datetime.timedelta(seconds=time.time() - st)}\n")


if __name__ == "__main__":
    # creating csv for spellgram data
    spg_data = pd.read_csv(SPG_DATA_PATH)
    spg_correct = spg_data['target']
    spg_incorrect = spg_data['source']
    spg_predicted = read_file(SPG_PREDICTED)
    create_csv(
        spg_correct,
        spg_incorrect,
        spg_predicted,
        SPG_CSV_PATH,
    )

    # creating csv for github-typo-corpus data
    gtc_correct = read_file(GTC_CORRECT)
    gtc_incorrect = read_file(GTC_INCORRECT)
    gtc_predicted = read_file(GTC_PREDICTED)
    create_csv(
        gtc_correct,
        gtc_incorrect,
        gtc_predicted,
        GTC_CSV_PATH,
    )

    # custom trained
    gtc_predicted = read_file(GTC_CUS_PREDICTED)
    create_csv(
        gtc_correct,
        gtc_incorrect,
        gtc_predicted,
        GTC_CUS_CSV_PATH,
    )

