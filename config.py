import torch
import os

# --------------------------------------------------------------------------
# Define 5-class sentiment mapping
SENTIMENT_MAPPING = {
    0: "Horrible",
    1: "Really Negative",
    2: "Negative",
    3: "Neutral",
    4: "Positive",
    5: "Really Positive",
}

SENTIMENT_MAPPING_3_LABEL_VERSION = {
    1: "Negative",
    2: "Neutral",
    3: "Positive",
}

LABEL_MAPPING = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5}

# --------------------------------------------------------------------------
# Model config
TOKENIZER_NAME = "bert-base-uncased"
MODEL_NAME = "bert-base-uncased"

EPOCHS = 10
N_CLASSES = 6
DROPOUT = 0.3
MAX_LEN = 128
TEST_SIZE = 0.1
VAL_SIZE = 0.1
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --------------------------------------------------------------------------
# Real Dataset paths
DATASET_PATH = "Dataset/text.csv"

# --------------------------------------------------------------------------
# Model config

# outpus paths
MODEL_TRAINING_OUTPUT_DIR = "outputs/training_evaluation/training"
MODEL_EVALUATION_OUTPUT_DIR = "outputs/training_evaluation/evaluation"

# -------------------------------------------------------------------------
# Test dataset folder path
TEST_DATA_DIR = "dataset/test_datasets"  # folder containing test data files
os.makedirs(TEST_DATA_DIR, exist_ok=True)

