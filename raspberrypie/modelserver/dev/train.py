import torch
import torch.nn as nn
from torchvision import datasets, transforms
from autoencoder import Autoencoder
from pathlib import Path
import pandas as pd
import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

def train():
    # Setup training data
    url = 'http://localhost:8086'
    username = ''
    password = ''
    token = f'{username}:{password}'

    database = 'features'
    retention_policy = 'autogen'
    bucket = f'{database}/{retention_policy}'

    client = InfluxDBClient(url=url, token=token)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    query_api = client.query_api()

    query = f'from(bucket: "{bucket}")\
    |> range(start: -1y)\
    |> tail(n: 10000)\
    |> filter(fn: (r) => r["_field"] == "feature")'
    df = query_api.query_data_frame(query)
    output = []
    for feature in df['_value']:
        f = np.fromstring(feature, sep='\n', dtype=np.float32)
        output.append(f)
    output = np.array(output)

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