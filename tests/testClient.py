import torch
from torchvision import datasets, transforms
from pathlib import Path
import requests
import json

mnist_data = datasets.MNIST(root=Path() / 'data', train=False, download=True, transform=transforms.ToTensor())
data_loader = torch.utils.data.DataLoader(dataset=mnist_data, batch_size=1, shuffle=False)

url = 'http://localhost:9000/evalloss'
jsonData = json.dumps(mnist_data[0][0].reshape(-1, 28*28).tolist())
response = requests.post(url, jsonData)
print(response.text)