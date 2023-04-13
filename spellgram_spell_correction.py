import os
import pandas as pd
from transformers import pipeline

CSV_PATH = "./data/spellgram.csv"


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

    spellgram = pd.read_csv(CSV_PATH)

    source = spellgram["source"]
    target = spellgram["target"]

    predicted_lines = []
    count = 0
    for line in source:

        predicted_lines.append(
            fix_spelling(
                line,
                max_length=2048
            )[0]["generated_text"]
        )

        print(f"{count} / {len(source)}", end='\r', flush=True)
        count += 1

    if len(predicted_lines):
        # save(f"./data/predicted/spellgram-predicted-{count}.txt", predicted_lines)
        pass

