import matplotlib.pyplot as plt
import pandas as pd

DEV = False
IS_CUSTOM = True

if DEV:
    GTC_CSV = "./data/gtc-small-similarity.csv"
elif IS_CUSTOM:
    GTC_CSV = "./data/gtc-custom-similarity.csv"
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
        if data.get('cis')[i] <= data.get('cps')[i]:
            gl.append(dp)
            gc += 1
            continue
        bl.append(dp)
        bc += 1

    return gc, bc, gl, bl


def create_bins(data: dict):
    """Create bins based on line length.
    Based on the data in ./data/gtc-small-similarity.csv, there are 39 length sizes

    Arg:
        data: dictionary read from ./data/gtc-small-similarity.csv

    Returns:
        bin: dictionary containing bins

    """
    max_lens = set()
    for i in range(len(data.get('p'))):
        max_lens.add(
            max(
                len(str(data.get('c')[i])),
                len(str(data.get('i')[i])),
                len(str(data.get('p')[i]))
            )
        )

    max_lens = sorted(max_lens)
    num_bins = 5
    seperation = len(max_lens) / num_bins

    def divide_chunks(l, n):

        # looping till length l
        for i in range(0, len(l), n):
            yield l[i:i + n][-1]

    x = list(divide_chunks(max_lens, int(seperation)))
    print(len(max_lens))
    print(x)

    if len(max_lens) % num_bins == 0:
        seperation = int(seperation)
    else:
        seperation = int(len(max_lens) / (num_bins - 1))

    bins = set(max_lens[seperation::seperation])
    print(bins)
    bins.add(max_lens[len(max_lens) - 1])
    bins = sorted(bins)
    print(bins)

    tmp_bin = {}
    for b in bins:
        tmp_bin[b] = {'c': [], 'i': [], 'p': [], 'cis': [], 'cps': [], 'ips': []}

    bins = tmp_bin

    for i in range(len(data.get('c'))):
        cor, inc, prd = str(data.get('c')[i]), str(data.get('i')[i]), str(data.get('p')[i])
        max_len = max(len(cor), len(inc), len(prd))
        bin_keys = list(bins.keys())
        for idx in range(len(bin_keys) - 1):
            if idx == 0:
                if 0 < max_len <= bin_keys[0]:
                    bins[bin_keys[0]]['c'].append(cor)
                    bins[bin_keys[0]]['i'].append(inc)
                    bins[bin_keys[0]]['p'].append(prd)
                    bins[bin_keys[0]]['cis'].append(data.get('cis')[i])
                    bins[bin_keys[0]]['cps'].append(data.get('cps')[i])
                    bins[bin_keys[0]]['ips'].append(data.get('ips')[i])
                    continue
            if bin_keys[idx] < max_len <= bin_keys[idx + 1]:
                bins[bin_keys[idx + 1]]['c'].append(cor)
                bins[bin_keys[idx + 1]]['i'].append(inc)
                bins[bin_keys[idx + 1]]['p'].append(prd)
                bins[bin_keys[idx + 1]]['cis'].append(data.get('cis')[i])
                bins[bin_keys[idx + 1]]['cps'].append(data.get('cps')[i])
                bins[bin_keys[idx + 1]]['ips'].append(data.get('ips')[i])

    return bins


def per(nu, de):
    return round((nu / de) * 100, 2)


if __name__ == "__main__":

    gtc_data = preprocess_csv(GTC_CSV)
    gtc_gc, gtc_bc, gtc_g_lines, gtc_b_lines = cis_gt_cps(gtc_data)
    print(f"gtc_good_prediction_count: {per(gtc_gc, len(gtc_data.get('p')))}%")
    print(f"gtc_bad_prediction_count: {per(gtc_bc, len(gtc_data.get('p')))}%")

    spg_data = preprocess_csv(SPG_CSV)
    spg_gc, spg_bc, spg_g_lines, spg_b_lines = cis_gt_cps(spg_data)
    print(f"spg_good_prediction_count: {per(spg_gc, len(spg_data.get('p')))}%")
    print(f"spg_bad_prediction_count: {per(spg_bc, len(spg_data.get('p')))}%")

    bins = create_bins(gtc_data)
    for k, v in bins.items():
        print(f"{k}: {len(v['c'])}")
        gc, bc, g_lines, b_lines = cis_gt_cps(v)
        print(f"good_prediction_count: {per(gc, len(v.get('p')))}%")
        print(f"bad_prediction_count: {per(bc, len(v.get('p')))}%")
        print()
