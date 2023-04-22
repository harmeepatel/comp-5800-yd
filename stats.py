import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.rcParams['figure.dpi'] = 128

DEV = True

GTC_CSV = "./data/gtc-similarity.csv"
CUS_GTC_CSV = "./data/gtc-custom-similarity.csv"
SPG_CSV = "./data/spg-similarity.csv"

COMP_MATRIC = "cp-gt-ci_cp-gt-ip"


def per(nu, de):
    return round((nu / de) * 100, 2)


def preprocess_csv(path):
    data = pd.read_csv(path)
    new_data = {}
    new_data['c'] = data['correct']
    new_data['i'] = data['incorrect']
    new_data['p'] = data['predicted']
    new_data['ciss'] = data['c-i-sim-spacy']
    new_data['cpss'] = data['c-p-sim-spacy']
    new_data['ipss'] = data['i-p-sim-spacy']
    new_data['cisb'] = data['c-i-sim-bleu']
    new_data['cpsb'] = data['c-p-sim-bleu']
    new_data['ipsb'] = data['i-p-sim-bleu']

    return new_data


def pred_classification(data_len, cis, cps, ips):
    """Checks the similarity between correct and incorrect sentence, and correct and predicted sentence.
    It is a good prediction if cor-inc similatiry is less than cor-prd similarity, else it is considered
    bad prediction

    Args:
        data: dictionary read from ./data/gtc-small-similarity.csv

    Returns:
        gc: good prediction count
        bc: bad prediction count

    """
    gc = 0
    bc = 0

    for i in range(data_len):
        if cps > cis and cps > ips:
            gc += 1
            continue
        bc += 1

    return gc, bc


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
        tmp_bin[b] = {
            'c': [],
            'i': [],
            'p': [],
            'ciss': [],
            'cpss': [],
            'ipss': [],
            'cisb': [],
            'cpsb': [],
            'ipsb': []
        }

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
                    bins[bin_keys[0]]['ciss'].append(data.get('ciss')[i])
                    bins[bin_keys[0]]['cpss'].append(data.get('cpss')[i])
                    bins[bin_keys[0]]['ipss'].append(data.get('ipss')[i])
                    bins[bin_keys[0]]['cisb'].append(data.get('cisb')[i])
                    bins[bin_keys[0]]['cpsb'].append(data.get('cpsb')[i])
                    bins[bin_keys[0]]['ipsb'].append(data.get('ipsb')[i])
                    continue
            if bin_keys[idx] < max_len <= bin_keys[idx + 1]:
                bins[bin_keys[idx + 1]]['c'].append(cor)
                bins[bin_keys[idx + 1]]['i'].append(inc)
                bins[bin_keys[idx + 1]]['p'].append(prd)
                bins[bin_keys[idx + 1]]['ciss'].append(data.get('ciss')[i])
                bins[bin_keys[idx + 1]]['cpss'].append(data.get('cpss')[i])
                bins[bin_keys[idx + 1]]['ipss'].append(data.get('ipss')[i])
                bins[bin_keys[idx + 1]]['cisb'].append(data.get('cisb')[i])
                bins[bin_keys[idx + 1]]['cpsb'].append(data.get('cpsb')[i])
                bins[bin_keys[idx + 1]]['ipsb'].append(data.get('ipsb')[i])

    return bins


def plot_bins(data, save_path, sim='spacy'):
    bins = create_bins(data)
    bin_keys = list(bins.keys())
    g_bin_count = []
    b_bin_count = []

    for _, v in bins.items():
        match sim:
            case 'spacy':
                gc, bc = pred_classification(data_len=len(data.get('c')), cis=v['ciss'], cps=v['cpss'], ips=v['ipss'])
            case 'bleu':
                gc, bc = pred_classification(data_len=len(data.get('c')), cis=v['cisb'], cps=v['cpsb'], ips=v['ipsb'])

        g_bin_count.append(gc)
        b_bin_count.append(bc)

    x_axis = np.arange(len(bin_keys))

    plt.bar(x_axis - 0.2, g_bin_count, 0.4, label='good', color='yellowgreen')
    plt.bar(x_axis + 0.2, b_bin_count, 0.4, label='bad', color='tomato')
    plt.xticks(x_axis, bin_keys)
    # plt.yscale('log')
    plt.xlabel("Sentence Length")
    plt.ylabel("Number of Sentence")

    if DEV:
        plt.show()
    else:
        plt.savefig(save_path, bbox_inches="tight")


if __name__ == "__main__":

    print(f"__{COMP_MATRIC}__")
    gtc_data = preprocess_csv(GTC_CSV)
    gtc_gc, gtc_bc = pred_classification(gtc_data)
    print(
        (f"gtc_good_prediction_count: {per(gtc_gc, len(gtc_data.get('p')))}%\n"
         f"gtc_bad_prediction_count: {per(gtc_bc, len(gtc_data.get('p')))}%\n")
    )

    cus_gtc_data = preprocess_csv(CUS_GTC_CSV)
    cus_gtc_gc, cus_gtc_bc = pred_classification(cus_gtc_data)
    print(
        (f"cus_gtc_good_prediction_count: {per(cus_gtc_gc, len(cus_gtc_data.get('p')))}%\n"
         f"cus_gtc_bad_prediction_count: {per(cus_gtc_bc, len(cus_gtc_data.get('p')))}%\n")
    )

    spg_data = preprocess_csv(SPG_CSV)
    spg_gc, spg_bc = pred_classification(spg_data)
    print(
        (f"spg_good_prediction_count: {per(spg_gc, len(spg_data.get('p')))}%\n"
         f"spg_bad_prediction_count: {per(spg_bc, len(spg_data.get('p')))}%\n")
    )

    total_g = [gtc_gc, cus_gtc_gc, spg_gc]
    total_b = [gtc_bc, cus_gtc_bc, spg_bc]
    x_axis = np.arange(len(total_g))

    plt.bar(x_axis - 0.2, total_g, 0.4, label='good', color='yellowgreen')
    plt.bar(x_axis + 0.2, total_b, 0.4, label='bad', color='tomato')
    plt.xticks(x_axis, ['github-typo-corpus-pretrained-spacy-similarity',
               'github-typo-corpus-custom-trained-spacy-similarity', 'spellgram-pretrained-spacy-similarity'])
    # plt.yscale('log')
    plt.xlabel("Data")
    plt.ylabel("Number of Sentence")
    plt.legend()
    # plt.title(("cor-inc-similarity < cor-prd-similarity and inc-prd-similarity < cor-prd-similarity"))
    if DEV:
        plt.show()
    else:
        plt.savefig(f"./plot-fig/total-{COMP_MATRIC}.png", bbox_inches="tight")

    # Bins
    plot_bins(gtc_data, f"./plot-fig/pretrained-{COMP_MATRIC}.png")
    plot_bins(cus_gtc_data, f"./plot-fig/custom-{COMP_MATRIC}.png")
