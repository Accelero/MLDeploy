import torch
from torchvision import datasets, transforms
from pathlib import Path
import requests
import json
import pandas as pd

data_path = "C:/Users/David/Nextcloud/MA David/Datensätze/HELLER-Data-Full.csv"
df = pd.read_csv(data_path)
features = df.iloc[:, :-1]

url = 'http://localhost:9000/evalloss'
jsonData = json.dumps(features.sample().values.tolist())
response = requests.post(url, jsonData)
print(response.text)