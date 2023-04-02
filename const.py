T_DATA = "./data/gtc-small-incorrect-correct.txt"
DATA = "./data/gtc-incorrect-correct.txt"

MAX_CHAR_LEN = 4
BOS = '<START>'
EOS = '<END>'
PAD = '<PAD>'
OOV = '<OOV>'

UNITS = 128
EPOCH = 10
BUFFER_SIZE = 32000
BATCH_SIZE = 64
# Let's limit the #training examples for faster training
NUM_EXAMPLES = 30000
