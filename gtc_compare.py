import datetime
import pandas as pd
import spacy
import time

DEV = True
if DEV:
    PREDICTED = "./data/predicted/predicted-10000.txt"
    CSV_PATH = "./data/gtc-small-similarity.csv"
else:
    PREDICTED = "./data/gtc-predicted.txt"
    CSV_PATH = "./data/gtc-similarity.csv"

CORRECT = "./data/gtc-correct.txt"
INCORRECT = "./data/gtc-incorrect.txt"
nlp = spacy.load("en_core_web_lg")


def read_file(path):
    lines = []
    with open(path, 'r') as f:
        lines = f.readlines()

    return lines


def save_file(path, data):
    with open(path, '+w') as f:
        f.writelines(data)


if __name__ == "__main__":
    st = time.time()

    bc = 0
    c = 0
    ue = 0

    correct, incorrect, predicted = read_file(CORRECT), read_file(INCORRECT), read_file(PREDICTED)

    min_val = min(len(correct), len(incorrect), len(predicted))
    lines = {
        'correct': [],
        'incorrect': [],
        'predicted': [],
        'incorrect-correct-similarity': [],
        'incorrect-predicted-similarity': [],
        'correct-predicted-similarity': [],
    }
    t = time.time()
    iter_sec = 0
    for i in range(min_val):
        c_line = correct[i].strip()
        i_line = incorrect[i].strip()
        p_line = predicted[i].strip()

        if DEV:
            if ue == 2000:
                break
            else:
                ue += 1

        if ue % 200 == 0:
            iter_sec = 200 / (time.time() - t)
            t = time.time()

        cor_vec = nlp(c_line)
        inc_vec = nlp(i_line)
        pre_vec = nlp(p_line)

        # print(f"c[{i}]:", cor_vec, "<->", f"i[{i}]:", inc_vec, cor_vec.similarity(inc_vec))
        # print(f"p[{i}]:", pre_vec, "<->", f"i[{i}]:", inc_vec, pre_vec.similarity(inc_vec))
        print(f"{i} / {min_val} [ {round(iter_sec, 4)} itr/s ]", end='\r')

        i_c_sim = inc_vec.similarity(cor_vec)
        i_p_sim = inc_vec.similarity(pre_vec)
        c_p_sim = cor_vec.similarity(pre_vec)

        lines['correct'].append(f"{c_line}")
        lines['incorrect'].append(f"{i_line}")
        lines['predicted'].append(f"{p_line}")
        lines['incorrect-correct-similarity'].append(str(i_c_sim))
        lines['incorrect-predicted-similarity'].append(str(i_p_sim))
        lines['correct-predicted-similarity'].append(str(c_p_sim))

        if (i_c_sim > i_p_sim):
            bc += 1
            continue
        c += 1

    df = pd.DataFrame(lines)
    df.to_csv(CSV_PATH, index=False)

    print(f"\ngood predictions: {c}")
    print(f"bad predictions:  {bc}")

    print(f"time taken: {datetime.timedelta(seconds=time.time() - st)}")
