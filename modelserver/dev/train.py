import torch
import torch.nn as nn
from torchvision import datasets, transforms
from autoencoder import Autoencoder
from pathlib import Path
import pandas as pd
import numpy as np

def train():
    # Setup training data
    data_path = './data/testset.csv'
    df = pd.read_csv(data_path)
    df = df.iloc[3:, 6]
    df = pd.to_numeric(df)
    index = 0
    output = []
    while index in range(0, len(df.index)):
        temp=df.iloc[index:index+512]
        if len(temp)==512:
            output.append(temp.to_list())
        index = index+10

    training_data = torch.tensor(output, dtype=torch.float32)
    data_loader = torch.utils.data.DataLoader(dataset=training_data, batch_size=16, shuffle=True)


    # Setup training parameters
    model = Autoencoder()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    num_epochs = 200

    # Training
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
    torch.save(model.state_dict(), "app/autoencoder.pt")
    torch.onnx.export(model, 
                      input, 
                      "app/autoencoder.onnx", 
                      input_names=['input'], 
                      output_names=['output'], 
                      dynamic_axes={'input':{0: 'batch_size'}, 
                                    'output':{0 : 'batch_size'}})

if __name__ == '__main__':
    train()