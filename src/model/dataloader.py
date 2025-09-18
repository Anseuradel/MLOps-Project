import os
import torch
import pandas as pd

from typing import Dict, Any
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizerBase

class SentimentDataset(Dataset):
    def __init__(self, reviews, labels, tokenizer, max_len=128):
        self.reviews = reviews
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.reviews)

    def __getitem__(self, idx):
        reviews = str(self.reviews[idx])
        label = self.labels[idx]

        encoding = self.tokenizer.encode_plus(
            reviews,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors="pt",
        )

        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long),
        }


def create_dataloader(df, tokenizer, max_len, batch_size):
    # Load pretrained tokenizer
    tokenizer = PreTrainedTokenizerBase

    #Convert labels to tensor
    labels = torch.tensor(df["label"].astype(int).to_numpy(), dtype=torch.long)

    dataset = SentimentDataset(
        reviews=df["text"].to_numpy(),
        labels=labels,
        tokenizer=tokenizer,
        max_len=max_len,
    )

    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True
    ) 
