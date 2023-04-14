import matplotlib.pyplot as plt
import pandas as pd

GTC_CSV = "./data/gtc-similarity.csv"
SPG_CSV = "./data/spg-similarity.csv"


def preprocess_csv(path):
    data = pd.read_csv(path)
    new_data = {}
    new_data['c'] = data['correct']
    new_data['i'] = data['incorrect']
    new_data['p'] = data['predicted']
    new_data['ics'] = data['incorrect-correct-similarity']
    new_data['ips'] = data['incorrect-predicted-similarity']
    new_data['cps'] = data['correct-predicted-similarity']

    return new_data


def ics_gt_ips(data):
    gc = 0
    bc = 0
    gl = []
    bl = []

    for i in range(len(data.get('p'))):
        dp = [data.get('c')[i], data.get('i')[i], data.get('p')[i]]
        if data.get('ics')[i] > data.get('ips')[i]:
            bl.append(dp)
            bc += 1
            continue
        gl.append(dp)
        gc += 1

    return gc, bc, gl, bl


if __name__ == "__main__":

    gtc_data = preprocess_csv(GTC_CSV)

    gtc_gc, gtc_bc, _, _ = ics_gt_ips(gtc_data)

    print(f"good_prediction_count: {(gtc_gc/len(gtc_data.get('p'))*100)}%")
    print(f"bad_prediction_count: {(gtc_bc/len(gtc_data.get('p'))*100)}%")

    spg_data = preprocess_csv(SPG_CSV)
    spg_gc, spg_bc, _, _ = ics_gt_ips(spg_data)

    print(f"good_prediction_count: {(spg_gc/len(spg_data.get('p'))*100)}%")
    print(f"bad_prediction_count: {(spg_bc/len(spg_data.get('p'))*100)}%")
