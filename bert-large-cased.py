import json
from transformers import pipeline

# unmasker = pipeline('fill-mask', model='bert-large-cased')
# # output = unmasker("UglifyJS (JS compressor/beautifier in JavaScript) contains a complete JavaScript parser that exposes a simple API. It's heavily tested and used in some big projects (WebKit).")
# output = unmasker("hello my [MASK] is harmee, it was a nice [MASK].")
# print(json.dumps(output, indent=4))

fix_spelling = pipeline("text2text-generation", model="oliverguhr/spelling-correction-english-base")
print(fix_spelling("UglifyJS (JS compressor/beautifier in JavaScript) contains a complete JavaScript parsr that exposes a simple API. It's heavily teted and used in some big projects (WebKit).", max_length=2048))
