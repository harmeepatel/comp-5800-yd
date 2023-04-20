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


def cis_gt_cps(data: dict):
    """Checks the similarity between correct and incorrect sentence, and correct and predicted sentence.
    It is a good prediction if cor-inc similatiry is less than cor-prd similarity, else it is considered
    bad prediction

    Args:
        data: dictionary read from ./data/gtc-small-similarity.csv

    Returns:
        gc: good prediction count
        bc: bad prediction count
        gl: good prediction lines
        bl: bad prediction lines

    """
    gc = 0
    bc = 0
    gl = []
    bl = []

    for i in range(len(data.get('p'))):
        dp = {'c': data.get('c')[i], 'i': data.get('i')[i], 'p': data.get('p')[i]}
        if data.get('cis')[i] > data.get('cps')[i]:
            bl.append(dp)
            bc += 1
            continue
        gl.append(dp)
        gc += 1

    return gc, bc, gl, bl


def create_bins(data: dict):
    """Create bins based on line length.
    Based on the data in ./data/gtc-small-similarity.csv, there are 39 length sizes

    Arg:
        data: dictionary read from ./data/gtc-small-similarity.csv

    Returns:
        bin: dictionary containing bins

    """
    bin = {33: [], 70: [], 193: []}

    max_lens = set()
    for i in range(len(data.get('p'))):
        max_lens.add(
            max(
                len(data.get('c')[i]),
                len(data.get('i')[i]),
                len(data.get('p')[i])
            )
        )

    max_lens = sorted(max_lens)
    num_bins = 4
    seperation = len(max_lens) / num_bins
    if len(max_lens) % num_bins == 0:
        print("int")
        seperation = int(seperation)
    else:
        print("float")
        seperation = int(len(max_lens) / (num_bins - 1))

    print(seperation)
    bins = set(max_lens[seperation::seperation])
    bins.add(max_lens[len(max_lens) - 1])
    bins = sorted(bins)

    for i in range(len(data.get('c'))):
        cor, inc, prd = data.get('c')[i], data.get('i')[i], data.get('p')[i]
        max_len = max(len(cor), len(inc), len(prd))
        if max_len <= 33:
            bin.get(33).append({'c': cor, 'i': inc, 'p': prd})
        elif max_len > 33 and max_len <= 70:
            bin.get(70).append({'c': cor, 'i': inc, 'p': prd})
        elif max_len > 70 and max_len <= 193:
            bin.get(193).append({'c': cor, 'i': inc, 'p': prd})
    return bin


if __name__ == "__main__":

    gtc_data = preprocess_csv(GTC_CSV)
    gtc_gc, gtc_bc, gtc_g_lines, gtc_b_lines = cis_gt_cps(gtc_data)
    print(f"gtc_good_prediction_count: {round((gtc_gc/len(gtc_data.get('p'))*100), 2)}%")
    print(f"gtc_bad_prediction_count: {round((gtc_bc/len(gtc_data.get('p'))*100), 2)}%")

    spg_data = preprocess_csv(SPG_CSV)
    spg_gc, spg_bc, spg_g_lines, spg_b_lines = cis_gt_cps(spg_data)
    print(f"spg_good_prediction_count: {round((spg_gc/len(spg_data.get('p'))*100), 2)}%")
    print(f"spg_bad_prediction_count: {round((spg_bc/len(spg_data.get('p'))*100), 2)}%")

    bins = create_bins(gtc_data)
