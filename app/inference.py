import torch
from autoencoder import Autoencoder
import torch.nn as nn
from pathlib import Path

model = Autoencoder()
model.load_state_dict(torch.load(Path(__file__).parent / 'autoencoder.pt'))
model.eval()
criterion = nn.MSELoss()

@torch.no_grad()
def eval(inputData):
    inputData = torch.tensor(inputData)

    recon = model(inputData)
    loss = criterion(inputData, recon).item()
    return loss