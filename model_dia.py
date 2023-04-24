# import torch
# from transformers import BartModel
from torchviz import make_dot


# model = BartModel.from_pretrained("./sp_colab/models/bart-base-gtc", torchscript=True)
# print(model.eval())
# traced_model = torch.jit.trace(model, [tokens_tensor, segments_tensors])
# torch.jit.save(traced_model, "traced_bert.pt")
# make_dot(model)


from transformers import AutoTokenizer, BartModel
import torch

tokenizer = AutoTokenizer.from_pretrained("./sp_colab/models/bart-base-gtc")
model = BartModel.from_pretrained("./sp_colab/models/bart-base-gtc")

inputs = tokenizer("Hello, my dog is cute", return_tensors="pt")
outputs = model(**inputs)

print(inputs)
exit()
traced_model = torch.jit.trace(model, inputs)
torch.jit.save(traced_model, "traced_bert.pt")
make_dot(model)
# last_hidden_states = outputs.last_hidden_state
