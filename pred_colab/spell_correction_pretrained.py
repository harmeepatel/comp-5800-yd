import os
from tqdm import tqdm
from transformers import pipeline

DEV = True
if DEV:
    INCORRECT_PATH = "/content/pred_colab/data/inc.txt"
    FILE_NUM = 0
    SAVE_EVERY = 25
else:
    INCORRECT_PATH = "/content/pred_colab/data/gtc-incorrect.txt"
    FILE_NUM = 0
    SAVE_EVERY = 10_000

PRED_PATH = "/content/pred_colab/data/predicted"


def read_data(path):
    if not os.path.isfile(path):
        print(path)
    lines = open(path, encoding='utf-8').read().strip().split('\n')
    return lines


def save(path, data):
    """save data to file.

    Args:
        path (str): file path
        data ([[[int]]]): data to be saved
    """
    with open(path, 'w+') as f:
        for line in data:
            line = line.strip() + '\n'
            f.write(line)


if __name__ == "__main__":

    fix_spelling = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")

    incorrect_lines = read_data(INCORRECT_PATH)

    predicted_lines = []
    count = 0
    for line in tqdm(incorrect_lines):
        if DEV:
            if count > 50:
                break

        predicted_lines.append(
            fix_spelling(
                line,
                max_length=2048
            )[0]["generated_text"]
        )

        if count % SAVE_EVERY == 0 and count != 0 and count != FILE_NUM * SAVE_EVERY:
            if DEV:
                save(f"{PRED_PATH}/pretrained-predicted-small-{count}.txt", predicted_lines)
                pass
            else:
                save(f"{PRED_PATH}/pretrained-predicted-{count}.txt", predicted_lines)
                pass

            predicted_lines = []

        # print(f"{count} / {len(incorrect_lines)}", end='\r', flush=True)
        count += 1

    if len(predicted_lines):
        save(f"{PRED_PATH}/pretrained-predicted-{count}.txt", predicted_lines)
        pass

