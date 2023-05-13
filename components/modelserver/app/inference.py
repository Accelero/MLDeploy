import numpy as np
import onnx
import onnxruntime
from pathlib import Path

onnx_model = onnx.load('autoencoder.onnx')
onnx.checker.check_model(onnx_model)
ort_session = onnxruntime.InferenceSession('autoencoder.onnx')

# two input names exists due to the default input name of tensorflow is "input_1" but we usually assign "input" as input name in "pytorch"
input_name = 'input'
other_input_name = 'input_1'

def eval(inputData):
    try:
        ort_input = {input_name: inputData}
        recon = ort_session.run(None, ort_input)
    except:
        ort_input = {other_input_name: inputData}
        recon = ort_session.run(None, ort_input)
    loss = np.mean((recon-inputData)**2, axis=2)
    return loss