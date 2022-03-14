# Imports
import torch

import copy
import numpy as np
import pandas as pd
import seaborn as sns
from pylab import rcParams
import matplotlib.pyplot as plt
from matplotlib import rc
from sklearn.model_selection import train_test_split

from torch import nn, optim

import torch.nn.functional as F
from arff2pandas import a2p

# Specs
sns.set(style='whitegrid', palette='muted', font_scale=1.2)
HAPPY_COLORS_PALETTE = ["#01BEFE", "#FFDD00",
                        "#FF7D00", "#FF006D", "#ADFF02", "#8F00FF"]
sns.set_palette(sns.color_palette(HAPPY_COLORS_PALETTE))
rcParams['figure.figsize'] = 12, 8


def create_dataset(df):
    sequences = df.astype(np.float32).to_numpy().tolist()
    dataset = [torch.tensor(s).unsqueeze(1).float() for s in sequences]
    n_seq, seq_len, n_features = torch.stack(dataset).shape
    return dataset, seq_len, n_features

# Build Encoder


class Encoder(nn.Module):
    def __init__(self, seq_len, n_features, embedding_dim=64):
        super(Encoder, self).__init__()

        self.seq_len, self.n_features = seq_len, n_features
        self.embedding_dim, self.hidden_dim = embedding_dim, 2 * embedding_dim

        self.rnn1 = nn.LSTM(
            input_size=n_features,
            hidden_size=self.hidden_dim,
            num_layers=1,
            batch_first=True
        )

        self.rnn2 = nn.LSTM(
            input_size=self.hidden_dim,
            hidden_size=embedding_dim,
            num_layers=1,
            batch_first=True
        )

    def forward(self, x):
        x = x.reshape((1, self.seq_len, self.n_features))
        x, (_, _) = self.rnn1(x)
        x, (hidden_n, _) = self.rnn2(x)
        return hidden_n.reshape((self.n_features, self.embedding_dim))


# Build Decoder
class Decoder(nn.Module):
    def __init__(self, seq_len, input_dim=64, n_features=1):
        super(Decoder, self).__init__()

        self.seq_len, self.input_dim = seq_len, input_dim
        self.hidden_dim, self.n_features = 2 * input_dim, n_features

        self.rnn1 = nn.LSTM(
            input_size=input_dim,
            hidden_size=input_dim,
            num_layers=1,
            batch_first=True
        )

        self.rnn2 = nn.LSTM(
            input_size=input_dim,
            hidden_size=self.hidden_dim,
            num_layers=1,
            batch_first=True
        )

        self.output_layer = nn.Linear(self.hidden_dim, n_features)

    def forward(self, x):
        x = x.repeat(self.seq_len, self.n_features)
        x = x.reshape((self.n_features, self.seq_len, self.input_dim))

        x, (hidden_n, cell_n) = self.rnn1(x)
        x, (hidden_n, cell_n) = self.rnn2(x)
        x = x.reshape((self.seq_len, self.hidden_dim))

        return self.output_layer(x)


# Build AutoEncoder
class RecurrentAutoencoder(nn.Module):

    def __init__(self, seq_len, n_features, embedding_dim=64):
        super(RecurrentAutoencoder, self).__init__()
        device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")  # dirty fix

        self.encoder = Encoder(seq_len, n_features, embedding_dim).to(device)
        self.decoder = Decoder(seq_len, embedding_dim, n_features).to(device)

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)

        return x


# Training
def train_model(model, train_dataset, val_dataset, n_epochs):
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.L1Loss(reduction='sum').to(device)
    history = dict(train=[], val=[])
    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = 10000.0

    for epoch in range(1, n_epochs + 1):
        model = model.train()
        train_losses = []
        for seq_true in train_dataset:
            optimizer.zero_grad()
            seq_true = seq_true.to(device)
            seq_pred = model(seq_true)
            loss = criterion(seq_pred, seq_true)
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())

        val_losses = []
        model = model.eval()
        with torch.no_grad():
            for seq_true in val_dataset:
                seq_true = seq_true.to(device)
                seq_pred = model(seq_true)
                loss = criterion(seq_pred, seq_true)
                val_losses.append(loss.item())

        train_loss = np.mean(train_losses)
        val_loss = np.mean(val_losses)

        history['train'].append(train_loss)
        history['val'].append(val_loss)

        if val_loss < best_loss:
            best_loss = val_loss
            best_model_wts = copy.deepcopy(model.state_dict())

        print(f'Epoch {epoch}: train loss {train_loss} val loss {val_loss}')

    model.load_state_dict(best_model_wts)
    return model.eval(), history

# Prediction


def predict(model, dataset):
    predictions, losses = [], []
    criterion = nn.L1Loss(reduction='sum').to(device)
    with torch.no_grad():
        model = model.eval()
        for seq_true in dataset:
            seq_true = seq_true.to(device)
            seq_pred = model(seq_true)

            loss = criterion(seq_pred, seq_true)

            predictions.append(seq_pred.cpu().numpy().flatten())
            losses.append(loss.item())
    return predictions, losses


if __name__ == '__main__':
    # Specs
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    RANDOM_SEED = 42

    # Load model
    # GPU or CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Load model
    seq_len = 140  # hard coded is bad
    model = RecurrentAutoencoder(seq_len, 1, 128)
    model.load_state_dict(torch.load("myModel.pt"))
    model.eval()
    #model = model.to(device)

    # Import Data
    with open('ECGData/ECG5000_TRAIN.arff') as f:
        train = a2p.load(f)
    with open('ECGData/ECG5000_TEST.arff') as f:
        test = a2p.load(f)

    df = train.append(test)  # Merge train and test
    df = df.sample(frac=1.0)  # Shuffle data

    # Dataset consists of 5000 ECGs, each having a length of 140 values
    # Last column contains the label: 1 being normal 2-5 representing different anomalies
    CLASS_NORMAL = 1  # If value in last column == 1 then normal heartbeat
    new_columns = list(df.columns)  # Get list of columns
    new_columns[-1] = 'target'  # Rename last column to target
    df.columns = new_columns  # Update df columns

    # Move all normal heartbeats into a "normal_df"
    normal_df = df[df.target == str(CLASS_NORMAL)].drop(
        labels='target', axis=1)
    # Move all anomalous heartbeats into a "anomaly_df"
    anomaly_df = df[df.target != str(CLASS_NORMAL)].drop(
        labels='target', axis=1)

    # train_test_split
    train_df, val_df = train_test_split(
        normal_df,
        test_size=0.15,
        random_state=RANDOM_SEED
    )
    val_df, test_df = train_test_split(
        val_df,
        test_size=0.33,
        random_state=RANDOM_SEED
    )

    # Call method to create tensors for training, testing and validation
    train_dataset, seq_len, n_features = create_dataset(train_df)
    val_dataset, _, _ = create_dataset(val_df)
    test_normal_dataset, _, _ = create_dataset(test_df)
    test_anomaly_dataset, _, _ = create_dataset(anomaly_df)

    # # Choose threshold
    # _, losses = predict(model, train_dataset)
    # sns.distplot(losses, bins=50, kde=True);
    # Testing
    # _, losses = predict(model, ONE_ECG)
    #sns.distplot(losses, bins=50, kde=True);

    # Instantiate AutoEncoder
    model = RecurrentAutoencoder(seq_len, n_features, 128)
    model = model.to(device)

    print("Training starts now.")

    # Train the model
    model, history = train_model(
        model,
        train_dataset,
        val_dataset,
        n_epochs=20
    )

    print("Model successfully trained.")

    # Export model
    # Get I/O names
    inputOutputNames = np.round(np.linspace(1, 140, 140, endpoint=True))
    inputOutputNames = inputOutputNames.astype('U')
    seq_len = 140  # remove later
    # Create dummy input
    dummy_input = torch.randn(1, seq_len, requires_grad=True)
    # Export model
    torch.save(model.state_dict(), "myModel.pt")
