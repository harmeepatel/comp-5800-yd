import torch

model = torch.load('./sp/models/bart-base-en-mix/pytorch_model.bin', map_location=torch.device('cpu'))
model = model.eval()
