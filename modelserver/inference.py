# Description:
#   1) Import pre-trained ONNX model
#   2) Serve model via http using Flask
#   IH, 2022-03-02

# Imports
import onnxruntime as ort
import torch
from torch import nn
import numpy as np
import train


def predict(inputData):
    # Process inputData
    inputData = torch.tensor(inputData, dtype=torch.float32)
    inputData = inputData.reshape(([140, 1]))
    #inputData = inputData.numpy()
    # Rqe.: sess.run only provides model output i.e. the reconstructed ECG 140x1
    #result = session.run([output_name], {input_name: inputData})
    #result = (np.array(result))[0]
    model = train.RecurrentAutoencoder(140, 1, 128)
    mkeys, ukeys = model.load_state_dict(torch.load("modelserver/myModel.pt", map_location=torch.device('cpu')))
    model.eval()
    result = model(inputData)
    # Rqe.: nn.L1Loss requires tensors
    criterion = nn.L1Loss(reduction='sum')
    loss = criterion(inputData, result)
    if loss < 30:
        msg = "Normal Process"
    else:
        msg = "Anomaly Detected"
    return msg