import os
import time
from transformers import pipeline

DEV = False
CUSTOM_TRAINING = True
if DEV:
    INCORRECT_PATH = "./data/inc.txt"
    FILE_NUM = 0
    SAVE_EVERY = 25
else:
    INCORRECT_PATH = "./data/gtc-incorrect.txt"
    FILE_NUM = 9
    SAVE_EVERY = 10_000

PRED_PATH = "./data/predicted"


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
    print(f"file saved: {path}")


if __name__ == "__main__":

    # fix_spelling = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")
    fix_spelling = pipeline("text2text-generation", model="./sp/models/bart-base-en-mix/")

    incorrect_lines = read_data(INCORRECT_PATH)

    predicted_lines = []
    count = 0
    ui = 4
    t = time.time()
    for line in incorrect_lines:
        if DEV:
            if count > 50:
                break

        if count > FILE_NUM * SAVE_EVERY:
            # predicted_lines.append(1)
            predicted_lines.append(
                fix_spelling(
                    line,
                    max_length=2048
                )[0]["generated_text"]
            )
            # pass

        if count % SAVE_EVERY == 0 and count != 0 and count > FILE_NUM * SAVE_EVERY:
            if DEV:
                # print(f"{PRED_PATH}/predicted-small-{count}.txt", len(predicted_lines))
                # pass
                if CUSTOM_TRAINING:
                    save(f"{PRED_PATH}/predicted-custom-small-{count}.txt", predicted_lines)
                else:
                    save(f"{PRED_PATH}/predicted-small-{count}.txt", predicted_lines)
            else:
                # print(f"{PRED_PATH}/predicted-small-{count}.txt", len(predicted_lines))
                # pass
                if CUSTOM_TRAINING:
                    save(f"{PRED_PATH}/predicted-custom-{count}.txt", predicted_lines)
                else:
                    save(f"{PRED_PATH}/predicted-{count}.txt", predicted_lines)

            predicted_lines = []

        if count % ui == 0:
            iter_sec = ui / (time.time() - t)
            t = time.time()
        print(f"{count} / {len(incorrect_lines)}    [ {round(iter_sec, 4)} itr/s ]", end='\r', flush=True)
        count += 1

    if len(predicted_lines):
        if CUSTOM_TRAINING:
            save(f"{PRED_PATH}/predicted-custom-{count}.txt", predicted_lines)
        else:
            save(f"{PRED_PATH}/predicted-{count}.txt", predicted_lines)
        # pass

