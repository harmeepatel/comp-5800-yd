import os
import re

DEV = False
IS_CUSTOM = True

DATA_PATH = "./data/predicted/"
if DEV:
    P_PATH = "./data/gtc-predicted-small.txt"
elif IS_CUSTOM:
    P_PATH = "./data/gtc-custom-predicted.txt"
else:
    P_PATH = "./data/gtc-predicted.txt"

predicted = []
for root, dirs, files in os.walk(DATA_PATH):
    file_nums = set()
    for file in files:
        if DEV:
            pf = ''.join(re.findall(r'predicted-small-\d+.txt', file))
        elif IS_CUSTOM:
            pf = ''.join(re.findall(r'predicted-custom-\d+.txt', file))
        else:
            pf = ''.join(re.findall(r'predicted-\d+.txt', file))
        if pf:
            fn = int(''.join(re.findall(r'\d+', pf)))
            file_nums.add(fn)

    # c = 0
    for f_num in sorted(file_nums):
        print(f"len(predicted): {len(predicted)}")  # , end='\r', flush=True)
        if DEV:
            pf = f"predicted-small-{f_num}.txt"
        elif IS_CUSTOM:
            pf = f"predicted-custom-{f_num}.txt"
        else:
            pf = f"predicted-{f_num}.txt"
        path = DATA_PATH + pf
        with open(path, 'r') as f:
            lines = f.readlines()
            # print(path)
            # print(f"lines[0]: {lines[0]}")
            # print(f"lines[{len(lines)-1}]: {lines[len(lines)-1]}")
            # print()
            predicted.extend(lines)

        # if c == 3:
        #     break
        # c += 1


# print(len(predicted))
# print(predicted[:10])
print(f"unique predicted: {len(set(predicted))}")

with open("./data/gtc-correct.txt", 'r') as f:
    print(f"unique correct: {len(set(f.readlines()))}")
with open("./data/gtc-incorrect.txt", 'r') as f:
    print(f"unique incorrect: {len(set(f.readlines()))}")

with open(P_PATH, 'w+') as pf:
    pf.writelines(predicted)
