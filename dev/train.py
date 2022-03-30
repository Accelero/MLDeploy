import torch
import torch.nn as nn
from torchvision import datasets, transforms
from autoencoder import Autoencoder
from pathlib import Path
import pandas as pd
import numpy as np

def train():
    # Setup MNIST training data
    data_path = "C:/Users/David/Nextcloud/MA David/Datensätze/HELLER-Data-Full.csv"
    df = pd.read_csv(data_path)
    features = df.iloc[:, :-1]
    labels = df.iloc[:, [-1]]

    train = torch.tensor(features.values, dtype=torch.float32)
    data_loader = torch.utils.data.DataLoader(dataset=train, batch_size=64, shuffle=True)


    # Setup training parameters
    model = Autoencoder()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    num_epochs = 10
    outputs = []

    # Training
    num_epochs = 1000
    outputs = []
    for epoch in range(num_epochs):
        for input in data_loader:
            recon = model(input)
            loss = criterion(recon, input)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    print(f'Epoch:{epoch+1}, Loss:{loss.item(): .4f}')
    outputs.append((epoch, input, recon))

    # Export model
    torch.save(model.state_dict(), 'app/autoencoder.pt')

if __name__ == '__main__':
    train()