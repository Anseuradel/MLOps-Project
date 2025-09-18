import os
import torch
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import matplotlib

matplotlib.use("Agg")

from tqdm import tqdm
from datetime import datetime
from torch import nn
from torch.nn import Module
from typing import Tuple, List
from torch.utils.data import DataLoader
from sklearn.metrics import confusion_matrix, classification_report

def evaluate(model: Module, data_loader: DataLoader, loss_fn: nn.Module, device: torch.device):
    """
    Evaluates the model on validation data.
    """
  
    model.eval()
    total_loss = 0
    correct_predictions = 0
    total_samples = 0

    all_y_true = []
    all_y_pred = []
    all_confidences = []

    with torch.no_grad():
        for batch in tqdm(data_loader, desc="Evaluating"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)

            loss = loss_fn(outputs, labels)
            total_loss += loss.item()

            probs = torch.softmax(outputs, dim=1)  # Convert logits to probabilities
            predictions = torch.argmax(probs, dim=1)

            correct_predictions += (predictions == labels).sum().item()
            total_samples += labels.size(0)

            # Store values for evaluation plots
            all_y_true.extend(labels.cpu().numpy())
            all_y_pred.extend(predictions.cpu().numpy())
            all_confidences.extend(
                probs.max(dim=1)[0].cpu().numpy()
            )  # Max confidence per prediction

    avg_loss = total_loss / len(data_loader)
    accuracy = correct_predictions / total_samples

    return avg_loss, accuracy, all_y_true, all_y_pred, all_confidences
