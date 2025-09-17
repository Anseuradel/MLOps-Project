import pandas as pd 
import numpy as np
import nltk
from nltk.corpus import stopwords

from conif import *

import re 
from sklearn.model_selection import train_test_split

tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)

def clean_text(text):
    text = text.lower()                                # lowercase
    text = re.sub(r"http\S+|www\S+|https\S+", '', text) # remove URLs
    text = re.sub(r"\W", " ", text)                     # remove punctuation
    text = re.sub(r"\s+", " ", text)                    # remove extra spaces
    text = regex.compile(r'\p{Emoji}').sub('', text)  # remove emoticones
    text = " ".join([word for word in text.split() if word not in stop_words])
    return text


def tokenize_texts(texts, max_length):
  
  tokenized = tokenizer(
        texts, padding=True, truncation=True, max_length=max_length, return_tensors="pt"
    )

    # Convert PyTorch tensors to lists so they work with Pandas
  return {
     "input_ids": tokenized["input_ids"].tolist(),
     "attention_mask": tokenized["attention_mask"].tolist(),
   }

def preprocess_data(df, test_size, max_length):
  # Ensure content column is cleaned
    df["content"] = df["content"].apply(clean_text)

    # Tokenize the cleaned text
    tokenized_data = tokenize_texts(df["content"].tolist(), max_length)

    # Add tokenized columns back to the dataframe
    df["input_ids"] = tokenized_data["input_ids"]
    df["attention_mask"] = tokenized_data["attention_mask"]

    # Split data into training and validation sets
    train_df, val_df = train_test_split(
        df, test_size=test_size, stratify=stratify_param, random_state=42
    )

    return train_df, val_df
