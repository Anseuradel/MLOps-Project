import os
import torch
import pandas as pd

from typing import Dict, Any
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizerBase

class MyDataset(Dataset):
    def __init__(self,
        reviews: pd.Series,
        targets: torch.Tensor,
        tokenizer: PreTrainedTokenizerBase,
        max_len: int
        ):
        """
        Initializes the dataset 
        
        Args:
        """
          
        self.reviews = reviews.tolist()
        self.targets = targets
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        """
        Returns the number of samples in the dataset.

        Returns:
            int: Length of the dataset.
        """
        return len(self.data)

    def __getitem__(self, idx):
        review = str(self.reviews[item])
        target = self.targets[item]

        encoding = self.tokenizer.encode_plus(
            review,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding="max_length",
            return_attention_mask=True,
            truncation=True,
            return_tensors="pt",
        )

        return {
            "review_text": review,
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "targets": target,
        }


def create_dataloader(df: pd.DataFrame, tokenizer: PreTrainedTokenizerBase, max_len: int, batch_size: int)
    """
    Creates a PyTorch DataLoader for batching review data.
    """
    if df.empty:  # Check if dataset is empty
          return DataLoader([], batch_size=batch_size)  # Return empty DataLoader safely
  
      # Convert labels to a tensor for efficiency
      targets = torch.tensor(df["score"].to_numpy(), dtype=torch.long)
  
      # Create dataset instance
      dataset = MyDataset(
          reviews=df["content"], targets=targets, tokenizer=tokenizer, max_len=max_len
      )
  
      # Create DataLoader with optimized settings
      return DataLoader(
          dataset,
          batch_size=batch_size,
          num_workers=os.cpu_count() - 1,  # Enable multiprocessing for better performance
          shuffle=True,
      )
