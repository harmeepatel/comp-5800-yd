import matplotlib.pyplot as plt
import pandas as pd

DEV = True

if DEV:
    GTC_CSV = "./data/gtc-small-similarity.csv"
else:
    GTC_CSV = "./data/gtc-similarity.csv"
SPG_CSV = "./data/spg-similarity.csv"


def preprocess_csv(path):
    data = pd.read_csv(path)
    new_data = {}
    new_data['c'] = data['correct']
    new_data['i'] = data['incorrect']
    new_data['p'] = data['predicted']
    new_data['cis'] = data['c-i-sim-spacy']
    new_data['cps'] = data['c-p-sim-spacy']
    new_data['ips'] = data['i-p-sim-spacy']

    return new_data


def ics_gt_ips(data):
    gc = 0
    bc = 0
    gl = []
    bl = []

    for i in range(len(data.get('p'))):
        dp = {'correct': data.get('c')[i], 'incorrect': data.get('i')[i], 'predicted': data.get('p')[i]}
        if data.get('cis')[i] > data.get('cps')[i]:
            bl.append(dp)
            bc += 1
            continue
        gl.append(dp)
        gc += 1

    return gc, bc, gl, bl


if __name__ == "__main__":

    gtc_data = preprocess_csv(GTC_CSV)
    gtc_gc, gtc_bc, gtc_g_lines, gtc_b_lines = ics_gt_ips(gtc_data)
    print(f"gtc_good_prediction_count: {(gtc_gc/len(gtc_data.get('p'))*100)}%")
    print(f"gtc_bad_prediction_count: {(gtc_bc/len(gtc_data.get('p'))*100)}%")

    spg_data = preprocess_csv(SPG_CSV)
    spg_gc, spg_bc, spg_g_lines, spg_b_lines = ics_gt_ips(spg_data)
    print(f"spg_good_prediction_count: {(spg_gc/len(spg_data.get('p'))*100)}%")
    print(f"spg_bad_prediction_count: {(spg_bc/len(spg_data.get('p'))*100)}%")
