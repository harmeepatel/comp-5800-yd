import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DEV = True

GTC_CSV = "./data/gtc-similarity.csv"
CUS_GTC_CSV = "./data/gtc-custom-similarity.csv"
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


def pred_classification(data: dict):
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
        if data.get('cis')[i] < data.get('cps')[i] and data.get('ips')[i] < data.get('cps')[i]:
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
    num_bins = 6
    seperation = len(max_lens) / num_bins

    if len(max_lens) % num_bins == 0:
        seperation = int(seperation)
    else:
        seperation = int(len(max_lens) / (num_bins - 1))

    bins = set(max_lens[seperation::seperation])
    bins.add(max_lens[len(max_lens) - 1])
    bins = sorted(bins)
    if bins[len(bins) - 1] - bins[len(bins) - 2] < 100:
        bins.remove(bins[len(bins) - 2])

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
    gtc_gc, gtc_bc, gtc_g_lines, gtc_b_lines = pred_classification(gtc_data)
    print(
        (f"gtc_good_prediction_count: {per(gtc_gc, len(gtc_data.get('p')))}%\n"
         f"gtc_bad_prediction_count: {per(gtc_bc, len(gtc_data.get('p')))}%\n")
    )

    cus_gtc_data = preprocess_csv(CUS_GTC_CSV)
    cus_gtc_gc, cus_gtc_bc, cus_gtc_g_lines, cus_gtc_b_lines = pred_classification(cus_gtc_data)
    print(
        (f"cus_gtc_good_prediction_count: {per(cus_gtc_gc, len(cus_gtc_data.get('p')))}%\n"
         f"cus_gtc_bad_prediction_count: {per(cus_gtc_bc, len(cus_gtc_data.get('p')))}%\n")
    )

    spg_data = preprocess_csv(SPG_CSV)
    spg_gc, spg_bc, spg_g_lines, spg_b_lines = pred_classification(spg_data)
    print(
        (f"spg_good_prediction_count: {per(spg_gc, len(spg_data.get('p')))}%\n"
         f"spg_bad_prediction_count: {per(spg_bc, len(spg_data.get('p')))}%\n")
    )
    fig, ax = plt.subplots()

    total_g = [gtc_gc, cus_gtc_gc, spg_gc]
    total_b = [gtc_bc, cus_gtc_bc, spg_bc]
    x_axis = np.arange(len(total_g))

    ax.bar(x_axis - 0.2, total_g, 0.4, label='good', color='yellowgreen')
    ax.bar(x_axis + 0.2, total_b, 0.4, label='bad', color='tomato')
    ax.set_yscale('log')

    plt.xticks(x_axis, ['gtc-pretrained', 'gtc-custom-trained', 'spg-pretrained'])
    plt.xlabel("Data")
    plt.ylabel("Number of Sentence")
    # plt.title(("cor-inc-similarity < cor-prd-similarity and inc-prd-similarity < cor-prd-similarity"))
    if DEV:
        plt.show()
    else:
        plt.savefig("./plot-fig/total.png")
    plt.legend()

    # Bins
    bins = create_bins(gtc_data)
    bin_keys = list(bins.keys())
    g_bin_count = []
    b_bin_count = []

    for k, v in bins.items():
        print(f"__{k}__: {len(v['c'])}")
        gc, bc, _, _ = pred_classification(v)
        g_bin_count.append(gc)
        b_bin_count.append(bc)

    n_bins = len(bin_keys)

    fig = plt.figure(dpi=256)
    ax0 = plt.add_subplot()
    x_axis = np.arange(len(bin_keys))

    ax0.bar(x_axis - 0.2, g_bin_count, 0.4, label='good', color='yellowgreen')
    ax0.bar(x_axis + 0.2, b_bin_count, 0.4, label='bad', color='tomato')
    ax0.set_yscale('log')

    extent = ax0.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    plt.xticks(x_axis, bin_keys)
    plt.xlabel("Sentence Length")
    plt.ylabel("Number of Sentence")
    # plt.title(("cor-inc-similarity < cor-prd-similarity and inc-prd-similarity < cor-prd-similarity"))
    plt.legend()
    if DEV:
        plt.show()
    else:
        fig.savefig('./plot-fig/custom-cis-lt-cps_ips-lt-cps.png', bbox_inches=extent.expanded(1, 1))
    # plt.savefig("./plot-fig/cis-lt-cps-and-ips-lt-cps.png")


