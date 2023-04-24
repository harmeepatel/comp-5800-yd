import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd
import os

mpl.rcParams['figure.dpi'] = 256
plt.rcParams['figure.figsize'] = [8, 4]

DEV = False

if DEV:
    GTC_CSV = "/content/sp_colab/data/csv/gtc-small-similarity.csv"
    CUS_GTC_CSV = "/content/sp_colab/data/csv/gtc-small-custom-similarity.csv"
    SPG_CSV = "/content/sp_colab/data/csv/spg-small-similarity.csv"
else:
    GTC_CSV = "/content/sp_colab/data/csv/gtc-similarity.csv"
    CUS_GTC_CSV = "/content/sp_colab/data/csv/gtc-custom-similarity.csv"
    SPG_CSV = "/content/sp_colab/data/csv/spg-similarity.csv"

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
        if cps[i] > cis[i] and cps[i] > ips[i]:
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


def get_total_counts():
    # using spacy (en_core_web_lg) similatiry pretrained model used on github-typo-corpus
    gtc_gc_spacy, gtc_bc_spacy = pred_classification(
        data_len=len(gtc_data.get('p')),
        cis=gtc_data.get('ciss'),
        cps=gtc_data.get('cpss'),
        ips=gtc_data.get('ipss')
    )

    # using spacy (en_core_web_lg) similatiry model trained with github-typo-corpus used on github-typo-corpus
    cus_gtc_gc_spacy, cus_gtc_bc_spacy = pred_classification(
        data_len=len(cus_gtc_data.get('p')),
        cis=cus_gtc_data.get('ciss'),
        cps=cus_gtc_data.get('cpss'),
        ips=cus_gtc_data.get('ipss')
    )

    # using spacy (en_core_web_lg) similatiry pretrained model used on spellgram
    spg_gc_spacy, spg_bc_spacy = pred_classification(
        data_len=len(spg_data.get('p')),
        cis=spg_data.get('ciss'),
        cps=spg_data.get('cpss'),
        ips=spg_data.get('ipss')
    )

    # using BLEU similatiry pretrained model used on github-typo-corpus
    gtc_gc_bleu, gtc_bc_bleu = pred_classification(
        data_len=len(gtc_data.get('p')),
        cis=gtc_data.get('cisb'),
        cps=gtc_data.get('cpsb'),
        ips=gtc_data.get('ipsb')
    )

    # using BLEU similatiry model trained with github-typo-corpus used on github-typo-corpus
    cus_gtc_gc_bleu, cus_gtc_bc_bleu = pred_classification(
        data_len=len(cus_gtc_data.get('p')),
        cis=cus_gtc_data.get('cisb'),
        cps=cus_gtc_data.get('cpsb'),
        ips=cus_gtc_data.get('ipsb')
    )

    # using BLEU similatiry pretrained model used on spellgram
    spg_gc_bleu, spg_bc_bleu = pred_classification(
        data_len=len(spg_data.get('p')),
        cis=spg_data.get('cisb'),
        cps=spg_data.get('cpsb'),
        ips=spg_data.get('ipsb')
    )

    g = [gtc_gc_spacy, gtc_gc_bleu, cus_gtc_gc_spacy, cus_gtc_gc_bleu, spg_gc_spacy, spg_gc_bleu]
    b = [gtc_bc_spacy, gtc_bc_bleu, cus_gtc_bc_spacy, cus_gtc_bc_bleu, spg_bc_spacy, spg_bc_bleu]

    return g, b


def plot(x_axis_len, x_ticks, green_data, red_data, save_path):
    fig, ax = plt.subplots()
    x_axis = np.arange(x_axis_len)

    ax.tick_params(axis='both', labelsize=6)
    width = 0.3

    bar1 = ax.bar(
        x_axis - (width / 2),
        green_data,
        label='good prediction count',
        color='yellowgreen',
        edgecolor='green',
        alpha=0.8,
        width=width,
    )
    bar2 = ax.bar(
        x_axis + (width / 2),
        red_data,
        label='bad prediction count',
        color='tomato',
        edgecolor='red',
        alpha=0.8,
        width=width,
    )

    i = 0
    per = []
    for gc, bc in zip(green_data, red_data):
        per.append(f"{round((gc / (gc + bc)) * 100, 2)}%")
    for gc, bc in zip(green_data, red_data):
        per.append(f"{round((bc / (gc + bc)) * 100, 2)}%")

    for rect in bar1 + bar2:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2.0, height, per[i], ha='center', va='bottom', fontsize=5)
        i += 1

    ax.set_xticks(x_axis, x_ticks)
    ax.set_xlabel("Sentence Length")
    ax.set_ylabel("Number of Sentence")
    ax.legend()

    if DEV:
        plt.show()
    else:
        print(f'saving: {save_path}')
        plt.savefig(save_path, bbox_inches="tight")


def plot_bins(data, save_path, sim='spacy'):
    bins = create_bins(data)
    bk1 = list(bins.keys())[:-1]
    bk1.insert(0, 0)
    bk2 = list(bins.keys())
    bin_keys = [f"{bk1[i]} - {bk2[i]}" for i in range(len(bins.keys()))]

    g_bin_count = []
    b_bin_count = []

    for k, v in bins.items():
        if (sim == 'spacy'):
            cis, cps, ips = v['ciss'], v['cpss'], v['ipss']
        elif (sim == 'bleu'):
            cis, cps, ips = v['cisb'], v['cpsb'], v['ipsb']

        gc, bc = pred_classification(data_len=len(v.get('c')), cis=cis, cps=cps, ips=ips)
        g_bin_count.append(gc)
        b_bin_count.append(bc)

    plot(
        x_axis_len=len(bin_keys),
        x_ticks=bin_keys,
        green_data=g_bin_count,
        red_data=b_bin_count,
        save_path=save_path
    )


if __name__ == "__main__":

    gtc_data = preprocess_csv(GTC_CSV)
    cus_gtc_data = preprocess_csv(CUS_GTC_CSV)
    spg_data = preprocess_csv(SPG_CSV)

    total_x_ticks = [
        'pretrained\nmodel\non GTC\nwith spacy\n(en_core_web_lg)\nsimilatiry',
        'pretrained\nmodel\non GTC\nwith BLEU\nsimilatiry',
        'GTC trained\nmodel\non GTC\nwith spacy\n(en_core_web_lg)\nsimilatiry',
        'GTC trained\nmodel\non GTC\nwith BLEU\nsimilatiry',
        'pretrained\nmodel\non SpellGram\nwith spacy\n(en_core_web_lg)\nsimilatiry',
        'pretrained\nmodel\non SpellGram\nwith BLEU\nsimilatiry'
    ]
    total_g, total_b = get_total_counts()

    os.makedirs(os.path.dirname("/content/sp_colab/plot-fig/total.png"), exist_ok=True)
    plot(
        x_axis_len=len(total_g),
        x_ticks=total_x_ticks,
        green_data=total_g,
        red_data=total_b,
        save_path="/content/sp_colab/plot-fig/total.png"
    )

    # Bins
    if not DEV:
        plot_bins(gtc_data, "/content/sp_colab/plot-fig/pretrained-spacy.png")
        plot_bins(cus_gtc_data, "/content/sp_colab/plot-fig/custom-spacy.png")

        plot_bins(gtc_data, "/content/sp_colab/plot-fig/pretrained-bleu.png", sim='bleu')
        plot_bins(cus_gtc_data, "/content/sp_colab/plot-fig/custom-bleu.png", sim='bleu')
