# Description:
#   1) Import pre-trained ONNX model
#   2) Serve model via http using Flask
#   IH, 2022-03-02

# Imports
import onnxruntime as ort
import torch
from torch import nn
from flask import Flask, jsonify, request
import numpy as np


# HTTP endpoint
app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def dataIO():
    # Get JSON from http message body
    inputData = request.get_json(force=True)
    # Go to predict() and return result message
    return jsonify(prediction(inputData))


def prediction(inputData):
    # Process inputData
    inputData = torch.tensor(inputData, dtype=torch.float32)
    inputData = inputData.reshape(([140, 1]))
    inputData = inputData.numpy()
    # Rqe.: sess.run only provides model output i.e. the reconstructed ECG 140x1
    result = session.run([output_name], {input_name: inputData})
    result = (np.array(result))[0]
    # Rqe.: nn.L1Loss requires tensors
    input4Loss = torch.tensor(inputData)
    output4Loss = torch.tensor(result)
    loss = criterion(input4Loss, output4Loss)
    if loss < 30:
        msg = "Normal Process"
    else:
        msg = "Anomaly Detected"
    return msg


if __name__ == '__main__':
    # Import ONNX model
    session = ort.InferenceSession("ECG_ONNX_MODEL.onnx", None)
    input_name = session.get_inputs()[0].name  # needed for session.run()
    output_name = session.get_outputs()[0].name  # needed for session.run()

    # Define loss function
    criterion = nn.L1Loss(reduction='sum')

    # Run REST Server
    app.run(host='0.0.0.0', port=9000, debug=True)
