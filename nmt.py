import numpy as np
import tensorflow as tf

correct_path = "./data/gmeg/dev/d/clean"
incorrect_path = "./data/gmeg/dev/d/corrupt"


correct = []
with open(correct_path, "r") as f:
    correct = [ lines.replace("\n", "") for lines in f.readlines()]

incorrect = []
with open(incorrect_path, "r") as f:
    incorrect = [ lines.replace("\n", "") for lines in f.readlines()]

correct, incorrect = np.array(correct), np.array(incorrect)

BUFFER_SIZE = len(correct)
BATCH_SIZE = 64

is_train = np.random.uniform(size=(len(incorrect),)) < 0.8

train_raw = (
    tf.data.Dataset
    .from_tensor_slices((correct[is_train], incorrect[is_train]))
    .shuffle(BUFFER_SIZE)
    .batch(BATCH_SIZE))
val_raw = (
    tf.data.Dataset
    .from_tensor_slices((correct[~is_train], incorrect[~is_train]))
    .shuffle(BUFFER_SIZE)
    .batch(BATCH_SIZE))

for i in train_raw:
    print(i)

# for example_context_strings, example_target_strings in train_raw.take(1):
#   print(example_context_strings[:5])
#   print()
#   print(example_target_strings[:5])
#   break
