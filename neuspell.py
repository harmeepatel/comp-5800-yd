import neuspell
from neuspell import BertChecker, CnnlstmChecker

checker_bert = BertChecker()
# Download BERT Pre-trained model
checker_bert.from_pretrained()

sen = checker_bert.correct("I luk foward to receving your reply")

print(sen)
