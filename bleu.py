from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.bleu_score import SmoothingFunction
import pandas as pd
import json
GTC_CSV_PATH = "./data/gtc-small-similarity.csv"


data = pd.read_csv(GTC_CSV_PATH)
cor = data['correct']
inc = data['incorrect']
prd = data['predicted']

w = (.33, .33, .33, 0)
smoothie = SmoothingFunction().method3

scores = []
for i in range(len(cor)):

    # print((
    #     f"c: {cor[i]}\n"
    #     f"i: {inc[i]}\n"
    #     f"p: {prd[i]}\n"
    # ))
    c = [str(cor[i]).split()]
    ii = [str(inc[i]).split()]
    io = str(inc[i]).split()
    p = str(prd[i]).split()
    ci = sentence_bleu(c, io, weights=w, smoothing_function=smoothie)
    cp = sentence_bleu(c, p, weights=w, smoothing_function=smoothie)
    ip = sentence_bleu(ii, p, weights=w, smoothing_function=smoothie)

    scores.append({'ci': ci, 'cp': cp, 'ip': ip})

print(json.dumps(scores[:10], indent=4))
