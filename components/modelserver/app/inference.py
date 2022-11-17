import numpy as np
import onnx
import onnxruntime
from pathlib import Path

onnx_model = onnx.load('autoencoder.onnx')
onnx.checker.check_model(onnx_model)
ort_session = onnxruntime.InferenceSession('autoencoder.onnx')

def eval(inputData):
    ort_input = {'input': inputData}
    recon = ort_session.run(None, ort_input)
    loss = np.mean((recon-inputData)**2, axis=2)
    return loss