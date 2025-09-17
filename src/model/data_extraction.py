import pandas as pd
import json 

from config import SENTIMENT_MAPPING, SENTIMENT_MAPPING_3_LABEL_VERSION, LABEL_MAPPING

def load_file_by_type(file_path):

    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)  # Load csv file
        elif file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return pd.DataFrame(data)  # Convert json to dataframe
        elif file_path.endswith(".xlsx"):
            return pd.read_excel(file_path, engine="openpyxl")  # Load Excel file
        else:
            raise ValueError(
                f"Unsupported file format : {file_path}. Only CSV, JSON, and XLSX are supported."
            )
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: File {file_path} not found.")


def merge_score_labels(score): 

  if score <= 1: 
    return 0 # Negative
  elif score ==2:
    return 1  # Neutral
  else:
    return 2 # positive


def load_data(file_path, merge_labels):

    try:
        df = load_file_by_type(file_path)

        # Check if required columns exist
        required_columns = {"text", "label"}
        if not required_columns.issubset(df.columns):
            raise ValueError("Dataset must contain 'text' and 'label' columns.")

        # Keep only relevant columns
        df = df[["text", "label"]].dropna()

        # ✅ Convert `score` values using `LABEL_MAPPING` (1-5 → 0-4)
        if not df["label"].isin(LABEL_MAPPING.keys()).all():
            raise ValueError(
                f"Dataset contains invalid score values. Allowed values: {sorted(LABEL_MAPPING.keys())}"
            )

        df["label"] = df["label"].map(LABEL_MAPPING)

        # If merge_labels is True, merge the labels into broader categories
        if merge_labels:
            df["label"] = df["label"].apply(merge_score_labels)
            df["label"] = df["label"].map(
                lambda x: SENTIMENT_MAPPING_3_LABEL_VERSION[x + 1]
            )
        else:
            df["label"] = df["label"].map(lambda x: SENTIMENT_MAPPING[x + 1])

        return df

    except FileNotFoundError as e:
        raise FileNotFoundError(e)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Error: File {file_path} is empty.")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")
