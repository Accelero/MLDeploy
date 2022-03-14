import torch.onnx
import pandas as pd
from Train import RecurrentAutoencoder
from torch import nn

if __name__ == "__main__":
    # Load PyTorch model
    model = RecurrentAutoencoder(140, 1, 128)
    model.load_state_dict(torch.load("myModel.pt"))
    # Set model to eval -> important
    model.eval()
    # print(model) # For reference
    # Load one input file (necessary step for export)
    oneECG = pd.read_csv("data.csv", header=None) # csv import
    oneECG = torch.tensor(oneECG.values, dtype=torch.float32) # convert to tensor
    oneECG = oneECG.to(device="cuda") # send tensor to GPU
    torch_out = model(oneECG) # generate output i.e. reconstructed 140x1 ECG
    torch.onnx.export(model, oneECG, "ECG_ONNX_MODEL.onnx", export_params=True, opset_version=10) # ONNX export

    

