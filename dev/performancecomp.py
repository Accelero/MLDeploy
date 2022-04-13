from multiprocessing import reduction
import onnx
import onnxruntime
import torch
import torch.nn as nn
from autoencoder import Autoencoder
from pathlib import Path
import pandas as pd
import numpy as np
import cProfile

torch_model = Autoencoder()
torch_model.load_state_dict(torch.load(Path(__file__).parent.parent / 'app/autoencoder.pt'))
torch_model.eval()
criterion = nn.MSELoss(reduction='none')

onnx_model = onnx.load(Path(__file__).parent.parent / 'app/autoencoder.onnx')
onnx.checker.check_model(onnx_model)
ort_session = onnxruntime.InferenceSession('app/autoencoder.onnx')

data_path = "C:/Users/David/Nextcloud/MA David/Datensätze/HELLER-Data-Full.csv"
df = pd.read_csv(data_path)
features = df.iloc[:, :-1]

@torch.no_grad()
def torchInf(inputData):
    inputData = torch.tensor(inputData)

    recon = torch_model(inputData)
    loss = np.mean((recon.numpy()-inputData.numpy())**2, axis=1)
    return loss

def onnxInf(inputData):
    ort_input = {'input': inputData}
    recon = ort_session.run(None, ort_input)
    loss = np.mean((recon-inputData)**2, axis=2)
    return loss

def batchData(batch_size):
    data = []
    for i in range(0, len(features.values), batch_size):
        data.append(features.values[i:i+batch_size].astype(np.float32))
    return data

def batchInf(func, batched_data):
    for batch in batched_data:
        func(batch)


if __name__=="__main__":
    batched_1 = batchData(1)
    batched_8 = batchData(8)
    batched_64 = batchData(64)
    batched_all = batchData(len(features))

    cProfile.run('batchInf(onnxInf, batched_1)', 'data/profiling/onnxtest/batch_1-6358_ONNX')
    cProfile.run('batchInf(onnxInf, batched_8)', 'data/profiling/onnxtest/batch_8-6358_ONNX')
    cProfile.run('batchInf(onnxInf, batched_64)', 'data/profiling/onnxtest/batch_64-6358_ONNX')
    cProfile.run('batchInf(onnxInf, batched_all)', 'data/profiling/onnxtest/batch_6358-6358_ONNX')

    cProfile.run('batchInf(torchInf, batched_1)','data/profiling/onnxtest/batch_1-6358_Pytorch')
    cProfile.run('batchInf(torchInf, batched_8)','data/profiling/onnxtest/batch_8-6358_Pytorch')
    cProfile.run('batchInf(torchInf, batched_64)', 'data/profiling/onnxtest/batch_64-6358_Pytorch')
    cProfile.run('batchInf(torchInf, batched_all)', 'data/profiling/onnxtest/batch_6358-6358_Pytorch')