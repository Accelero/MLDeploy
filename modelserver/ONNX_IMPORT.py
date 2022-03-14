import pandas as pd
import torch
import numpy as np
import onnx
from torch import nn
import onnxruntime as ort

# onnx_model = onnx.load("G:/Heider/01_Projekte/AutoLern/Tests/DEPLOY_2/EGC_ONNX_MODEL.onnx")
# onnx.checker.check_model(onnx_model)

input = pd.read_csv("data.csv", header=None)
input = input.to_numpy()
input = torch.tensor(input, dtype=torch.float32)
input = input.numpy()

# ONNX must be imported as InferenceSession
session = ort.InferenceSession("ECG_ONNX_MODEL.onnx", None)
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
print(input_name)
print(output_name)
result = session.run([output_name], {input_name: input})
# session.run only provides the model's output i.e. the AutoEncoder's reconstruction (140,1)

print("bpoint")
result = np.array(result)
print("bpoint2")
properFormatResult = result[0]
print("bpoint3")
# nn.L1Loss needs tensors as input
finalInput = torch.tensor(input)
finalOutput = torch.tensor(properFormatResult)
print("bpoint4")


criterion = nn.L1Loss(reduction='sum')
# input = input.tolist()
# result = result.tolist()
# Finally compute the loss
loss = criterion(finalInput, finalOutput)
print(loss)
print("end")