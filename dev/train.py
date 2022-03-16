import torch
import torch.nn as nn
from torchvision import datasets, transforms
from app.autoencoder import Autoencoder
from pathlib import Path

def train():
    # Setup MNIST training data
    transform = transforms.ToTensor()
    mnist_data = datasets.MNIST(root=Path() / 'data', train=True, transform=transform, download=True)
    data_loader = torch.utils.data.DataLoader(dataset=mnist_data, batch_size=64, shuffle=True)


    # Setup training parameters
    model = Autoencoder()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)
    num_epochs = 10
    outputs = []

    # Training
    for epoch in range(num_epochs):
        for(img, _) in data_loader:
            img = img.reshape(-1, 28*28)
            recon = model(img)
            loss = criterion(recon, img)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f'Epoch:{epoch+1}, Loss:{loss.item(): .4f}')
        outputs.append((epoch, img, recon))

    # Export model
    torch.save(model.state_dict(), 'modelserver/autoencoder.pt')

if __name__ == '__main__':
    train()