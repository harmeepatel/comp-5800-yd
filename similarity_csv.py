import datetime
import pandas as pd
import spacy
import time

DEV = True

SPG_DATA_PATH = "./data/spellgram.csv"
SPG_PREDICTED = "./data/predicted/spellgram-predicted-40000.txt"
if DEV:
    SPG_CSV_PATH = "./data/spg-small-similarity.csv"
else:
    SPG_CSV_PATH = "./data/spg-similarity.csv"


GTC_CORRECT = "./data/gtc-correct.txt"
GTC_INCORRECT = "./data/gtc-incorrect.txt"
GTC_PREDICTED = "./data/gtc-predicted.txt"
if DEV:
    GTC_CSV_PATH = "./data/gtc-small-similarity.csv"
else:
    GTC_CSV_PATH = "./data/gtc-similarity.csv"


nlp = spacy.load("en_core_web_lg")


def read_file(path):
    lines = []
    with open(path, 'r') as f:
        lines = f.readlines()

    return lines


def filter_none(data):
    return list(filter(lambda i: i is not None, data))


def create_csv(correct, incorrect, predicted, path):
    ue = 0
    ui = 50
    t = time.time()
    iter_sec = 0
    data_len = min(len(correct), len(incorrect), len(predicted))
    lines = {
        'correct': data_len * [None],
        'incorrect': data_len * [None],
        'predicted': data_len * [None],
        'incorrect-correct-similarity': data_len * [None],
        'incorrect-predicted-similarity': data_len * [None],
        'correct-predicted-similarity': data_len * [None],
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
        cor_vec = nlp(c_line)
        inc_vec = nlp(i_line)
        pre_vec = nlp(p_line)

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
        lines['incorrect-correct-similarity'][i] = inc_vec.similarity(cor_vec)
        lines['incorrect-predicted-similarity'][i] = inc_vec.similarity(pre_vec)
        lines['correct-predicted-similarity'][i] = cor_vec.similarity(pre_vec)

        if ue % ui == 0:
            iter_sec = ui / (time.time() - t)
            t = time.time()
        print(f"{i} / {data_len} [ {round(iter_sec, 4)} itr/s ]", end='\r')
        ue += 1

    lines['correct'] = filter_none(lines['correct'])
    lines['incorrect'] = filter_none(lines['incorrect'])
    lines['predicted'] = filter_none(lines['predicted'])
    lines['incorrect-correct-similarity'] = filter_none(lines['incorrect-correct-similarity'])
    lines['incorrect-predicted-similarity'] = filter_none(lines['incorrect-predicted-similarity'])
    lines['correct-predicted-similarity'] = filter_none(lines['correct-predicted-similarity'])

    pd.DataFrame(lines).to_csv(path, index=False)


if __name__ == "__main__":
    st = time.time()

    spg_data = pd.read_csv(SPG_DATA_PATH)
    spg_correct = spg_data['target']
    spg_incorrect = spg_data['source']
    spg_predicted = read_file(SPG_PREDICTED)

    create_csv(
        correct=spg_correct,
        incorrect=spg_incorrect,
        predicted=spg_predicted,
        path=SPG_CSV_PATH
    )

    gtc_correct = read_file(GTC_CORRECT)
    gtc_incorrect = read_file(GTC_INCORRECT)
    gtc_predicted = read_file(GTC_PREDICTED)
    create_csv(
        correct=gtc_correct,
        incorrect=gtc_incorrect,
        predicted=gtc_predicted,
        path=GTC_CSV_PATH
    )

    print(f"\ntime taken: {datetime.timedelta(seconds=time.time() - st)}")
