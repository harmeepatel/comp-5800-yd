import os
from transformers import pipeline
from tqdm import tqdm
# import threading
# from queue import Queue

Dev = True
if Dev:
    CORRECT_PATH = "./data/t.txt"
    INCORRECT_PATH = "./data/s.txt"
else:
    CORRECT_PATH = "./data/gtc-source.txt"
    INCORRECT_PATH = "./data/gtc-target.txt"

THREAD_COUNT = 8


def read_data(path):
    lines = open(path, encoding='utf-8').read().strip().split('\n')
    return lines


def save_npy(path, data):
    """save data to file.

    Args:
        path (str): file path
        data ([[[int]]]): data to be saved
    """
    [dir, file] = path.split('/')[1:]
    if not os.path.isdir(dir):
        os.mkdir(dir)
    if not os.path.isfile(file):
        open(path, 'w').close()

    with open(path, 'w+') as f:
        for line in data:
            line = line.strip() + '\n'
            f.write(line)


def get_corrected(line):
    return fix_spelling(
        line,
        max_length=2048
    )[0]["generated_text"]


if __name__ == "__main__":

    fix_spelling = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")

    correct_lines = read_data(CORRECT_PATH)
    incorrect_lines = read_data(INCORRECT_PATH)

    predicted_lines = []

    c = 0
    for line in tqdm(incorrect_lines):
        # if c == 10:
        #     break
        predicted_lines.append(
            fix_spelling(
                line,
                max_length=2048
            )[0]["generated_text"]
        )
        # c += 1

    print(predicted_lines)

    # q = Queue()
    #
    # for line in incorrect_lines:
    #     q.put(line)
    #
    # print("everythin in queue")
    #
    # threads = []
    #
    # print("starting to empty queue")
    # pbar = tqdm(total=len(incorrect_lines))
    # while not q.empty():
    #     lines = []
    #     for i in range(THREAD_COUNT):
    #         lines.append(q.get())
    #
    #     for x in range(THREAD_COUNT):
    #         t = threading.Thread(target=get_corrected, args=(lines[x],))
    #         threads.append(t)
    #         t.start()
    #
    #     for t in threads:
    #         t.join()
    #     pbar.update(THREAD_COUNT)

    save_npy("./data/predicted-small.txt", predicted_lines)



